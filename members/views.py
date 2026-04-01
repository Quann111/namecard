# ===== Standard library
import base64
import mimetypes
from urllib.parse import quote

# ===== Third-party
import qrcode
import cloudinary.uploader   # ✅ thêm import

# ===== Django
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template import loader
from django.urls import reverse
from django.utils.text import slugify

# ===== Local apps
from .models import Profile, Product
from .forms import ProfileForm, RegisterForm, LoginForm, ProductForm


def template_product(request):
    return render(request, "product.html")


def template_intro(request):
    return render(request, "intro.html", {
        "current_id": request.session.get("current_id")  # lấy lại id trước đó
    })


# Danh sách Profile
def members(request):
    profiles = Profile.objects.all().values()
    template = loader.get_template("template.html")
    context = {"profiles": profiles}
    return HttpResponse(template.render(context, request))


# --- DETAILS ---
def details(request, id):
    profile = get_object_or_404(Profile, id=id)
    # lưu vào session
    request.session["current_id"] = id  
    return render(request, "details.html", {
        "profile": profile,
        "current_id": id,
    })


def main(request):
    template = loader.get_template("main.html")
    return HttpResponse(template.render({}, request))


def testing(request):
    template = loader.get_template("template.html")
    context = {"fruits": ["Apple", "Banana", "Cherry"]}
    return HttpResponse(template.render(context, request))


# --- EDIT PROFILE ---
def edit_profile(request, id):
    profile = get_object_or_404(Profile, id=id)

    if "user_id" not in request.session or request.session["user_id"] != profile.id:
        messages.error(request, "Bạn không có quyền sửa thông tin này.")
        return redirect("details", id=id)

    form = ProfileForm(instance=profile)
    product_form = ProductForm()

    if request.method == "POST":
        # --- Xóa avatar ---
        if "delete_avatar" in request.POST:
            if profile.avatar:
                public_id = getattr(profile.avatar, "public_id", None)
                if public_id:
                    cloudinary.uploader.destroy(public_id)
                profile.avatar = None
                profile.save()
            messages.success(request, "Đã xóa avatar.")
            return redirect("edit_profile", id=profile.id)

        # --- Xóa background ---
        if "delete_background" in request.POST:
            if profile.background:
                public_id = getattr(profile.background, "public_id", None)
                if public_id:
                    cloudinary.uploader.destroy(public_id)
                profile.background = None
                profile.save()
            messages.success(request, "Đã xóa background.")
            return redirect("edit_profile", id=profile.id)

        # --- Cập nhật hồ sơ (bao gồm upload ảnh) ---
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            # Nếu có avatar mới -> xóa avatar cũ
            if request.FILES.get("avatar"):
                if profile.avatar:
                    public_id = getattr(profile.avatar, "public_id", None)
                    if public_id:
                        cloudinary.uploader.destroy(public_id)
                profile.avatar = request.FILES["avatar"]

            # Nếu có background mới -> xóa background cũ
            if request.FILES.get("background"):
                if profile.background:
                    public_id = getattr(profile.background, "public_id", None)
                    if public_id:
                        cloudinary.uploader.destroy(public_id)
                profile.background = request.FILES["background"]

            form.save()
            messages.success(request, "Cập nhật hồ sơ thành công!")
            return redirect("edit_profile", id=profile.id)

        # --- Thêm sản phẩm ---
        if "add_product" in request.POST:
            product_form = ProductForm(request.POST, request.FILES)
            if product_form.is_valid():
                product = product_form.save(commit=False)
                product.owner = profile
                product.save()
                messages.success(request, "Đã thêm sản phẩm mới!")
                return redirect("edit_profile", id=profile.id)

        # --- Cập nhật sản phẩm ---
        if "update_product" in request.POST:
            product_id = request.POST.get("product_id")
            product = get_object_or_404(Product, id=product_id, owner=profile)
            product.title = request.POST.get("title", product.title)
            product.description = request.POST.get("description", product.description)
            product.video_url = request.POST.get("video_url", product.video_url)
            if request.FILES.get("thumbnail"):
                product.thumbnail = request.FILES["thumbnail"]
            product.save()
            messages.success(request, "Cập nhật sản phẩm thành công!")
            return redirect("edit_profile", id=profile.id)

    products = profile.products.all()

    return render(request, "edit_profile.html", {
        "form": form,
        "profile": profile,
        "products": products,
        "product_form": product_form,
    })


# --- REGISTER ---
def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.save()
            messages.success(request, "Đăng ký thành công! Hãy đăng nhập.")
            return redirect("login")
    else:
        form = RegisterForm()
    return render(request, "register.html", {"form": form})


# --- LOGIN ---
# --- LOGIN ---
def login_view(request):
    # Nếu đã login rồi thì vào luôn trang edit_profile
    if request.session.get("user_id"):
        return redirect("edit_profile", id=request.session["user_id"])

    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]

            try:
                profile = Profile.objects.get(username=username)
                if check_password(password, profile.password):
                    request.session["user_id"] = profile.id
                    messages.success(request, "Đăng nhập thành công!")
                    return redirect("edit_profile", id=profile.id)
                else:
                    messages.error(request, "Sai mật khẩu!")
            except Profile.DoesNotExist:
                messages.error(request, "Tài khoản không tồn tại.")
    else:
        form = LoginForm()

    return render(request, "login.html", {"form": form})


# --- LOGOUT ---
def logout_view(request):
    request.session.flush()
    messages.success(request, "Bạn đã đăng xuất.")
    return redirect("login")


# --- VCF ---
def _fold(line, limit=75):
    if len(line) <= limit:
        return line
    return "\r\n ".join(line[i: i + limit] for i in range(0, len(line), limit))


def download_vcf(request, id):
    profile = get_object_or_404(Profile, id=id)
    full_name = profile.full_name or profile.username or "Contact"
    n_field = f"N:{full_name};;;;"

    lines = [
        "BEGIN:VCARD",
        "VERSION:3.0",
        _fold(n_field),
        _fold(f"FN:{full_name}"),
    ]

    if profile.company:
        lines.append(_fold(f"ORG:{profile.company}"))
    if profile.position:
        lines.append(_fold(f"TITLE:{profile.position}"))
    if profile.phone:
        lines.append(_fold(f"TEL;TYPE=CELL:{profile.phone}"))
    if profile.email:
        lines.append(_fold(f"EMAIL;TYPE=INTERNET:{profile.email}"))
    if profile.website:
        lines.append(_fold(f"URL:{profile.website}"))

    if profile.youtube:
        lines.append(_fold(f"X-SOCIALPROFILE;type=youtube:{profile.youtube}"))
    if profile.zalo:
        lines.append(_fold(f"X-SOCIALPROFILE;type=zalo:https://zalo.me/{profile.zalo}"))
    if profile.viber:
        lines.append(_fold(f"X-SOCIALPROFILE;type=viber:viber://chat?number={profile.viber}"))

    if profile.avatar:
        lines.append(_fold(f"PHOTO;VALUE=uri:{profile.avatar.url}"))

    lines.append("END:VCARD")
    vcf_content = "\r\n".join(lines) + "\r\n"

    safe = slugify(full_name) or "contact"
    quoted = quote(f"{full_name}.vcf")

    response = HttpResponse(vcf_content, content_type="text/vcard; charset=utf-8")
    response["Content-Disposition"] = (
        f"attachment; filename={safe}.vcf; filename*=UTF-8''{quoted}"
    )
    return response


# --- QR code ---
def qr_code(request, id):
    profile = get_object_or_404(Profile, id=id)
    detail_url = request.build_absolute_uri(f"/members/{profile.id}/")
    img = qrcode.make(detail_url)
    response = HttpResponse(content_type="image/png")
    img.save(response, "PNG")
    return response


# --- Tabs ---
def auth_tabs(request):
    ctx = {
        "login_form": LoginForm(),
        "register_form": RegisterForm(),
        "active_tab": "login",
    }
    return render(request, "auth_tabs.html", ctx)


# --- Product ---
def template_product(request, id):
    profile = get_object_or_404(Profile, id=id)
    request.session["current_id"] = id
    products = profile.products.all()
    return render(request, "product.html", {
        "profile": profile,
        "products": products,
        "current_id": id,
    })


def add_product(request, id):
    profile = get_object_or_404(Profile, id=id)
    if request.session.get("user_id") != profile.id:
        messages.error(request, "Bạn không có quyền thêm sản phẩm cho người khác.")
        return redirect("template_product", id=id)

    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.owner = profile
            product.save()
            return redirect("template_product", id=id)
    else:
        form = ProductForm()
    return render(request, "edit_product.html", {"form": form, "profile": profile})


def edit_product(request, id, product_id):
    product = get_object_or_404(Product, id=product_id, owner_id=id)
    if request.session.get("user_id") != product.owner.id:
        messages.error(request, "Bạn không có quyền sửa sản phẩm này.")
        return redirect("template_product", id=id)

    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect("template_product", id=id)
    else:
        form = ProductForm(instance=product)
    return render(request, "edit_product.html", {"form": form, "profile": product.owner})


def delete_product(request, id, product_id):
    product = get_object_or_404(Product, id=product_id, owner_id=id)
    if request.session.get("user_id") != product.owner.id:
        messages.error(request, "Bạn không có quyền xóa sản phẩm này.")
        return redirect("edit_profile", id=id)

    product.delete()
    return redirect("edit_profile", id=id)
