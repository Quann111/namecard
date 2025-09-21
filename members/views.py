# ===== Standard library
import base64
import mimetypes
from urllib.parse import quote

# ===== Third-party
import qrcode

# ===== Django
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template import loader
from django.urls import reverse
from django.utils.text import slugify
from .models import Product
from .forms import ProductForm

# ===== Local apps
from .forms import ProfileForm, RegisterForm, LoginForm
from .models import Profile

def template_product(request):
    return render(request, "product.html")

def template_intro(request):
    return render(request, "intro.html", {
        "current_id": request.session.get("user_id")  # truyền vào nếu có
    })

# Danh sách Profile
def members(request):
    profiles = Profile.objects.all().values()
    template = loader.get_template("template.html")
    context = {"profiles": profiles}
    return HttpResponse(template.render(context, request))


# --- DETAILS (ai cũng xem được) ---
def details(request, id):
    profile = get_object_or_404(Profile, id=id)
    return render(request, "details.html", {
        "profile": profile,
        "current_id": id,   # truyền id xuống template
    })

# Trang main
def main(request):
    template = loader.get_template("main.html")
    return HttpResponse(template.render({}, request))


# Ví dụ testing
def testing(request):
    template = loader.get_template("template.html")
    context = {"fruits": ["Apple", "Banana", "Cherry"]}
    return HttpResponse(template.render(context, request))


# --- EDIT PROFILE ---
def edit_profile(request, id):
    profile = get_object_or_404(Profile, id=id)

    # Check quyền
    if "user_id" not in request.session or request.session["user_id"] != profile.id:
        messages.error(request, "Bạn không có quyền sửa thông tin này.")
        return redirect("details", id=id)

    # ====== PROFILE UPDATE ======
    if request.method == "POST" and "save_profile" in request.POST:
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Cập nhật hồ sơ thành công!")
            return redirect("edit_profile", id=profile.id)
    else:
        form = ProfileForm(instance=profile)

    # ✅ luôn khởi tạo product_form mặc định
    product_form = ProductForm()

    # ====== ADD PRODUCT ======
    if request.method == "POST" and "add_product" in request.POST:
        product_form = ProductForm(request.POST, request.FILES)
        if product_form.is_valid():
            product = product_form.save(commit=False)
            product.owner = profile
            product.save()
            messages.success(request, "Đã thêm sản phẩm mới!")
            return redirect("edit_profile", id=profile.id)
    if request.method == "POST" and "save_profile" in request.POST:
        form = ProfileForm(request.POST, request.FILES, instance=profile)

        if "delete_avatar" in request.POST:
            profile.avatar = None
        if "delete_background" in request.POST:
            profile.background = None

        if form.is_valid():
            form.save()
            messages.success(request, "Cập nhật hồ sơ thành công!")
            return redirect("edit_profile", id=profile.id)

    # ====== UPDATE PRODUCT ======
    if request.method == "POST" and "update_product" in request.POST:
        product_id = request.POST.get("product_id")
        product = get_object_or_404(Product, id=product_id, owner=profile)
        product.video_url = request.POST.get("video_url", product.video_url)   # ✅ thêm dòng này

        product.title = request.POST.get("title", product.title)
        product.description = request.POST.get("description", product.description)
        if request.FILES.get("thumbnail"):
            product.thumbnail = request.FILES["thumbnail"]

        product.save()
        messages.success(request, "Cập nhật sản phẩm thành công!")
        return redirect("edit_profile", id=profile.id)

    # ====== Lấy danh sách sản phẩm ======
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
            # nếu dùng check_password khi login thì nhớ hash trước khi save
            profile.save()
            messages.success(request, "Đăng ký thành công! Hãy đăng nhập.")
            return redirect("login")
    else:
        form = RegisterForm()
    return render(request, "register.html", {"form": form})


# --- LOGIN ---
def login_view(request):
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
                    return redirect(reverse("edit_profile", args=[profile.id]))
                else:
                    messages.error(request, "Sai mật khẩu!")
            except Profile.DoesNotExist:
                messages.error(request, "Tài khoản không tồn tại.")
    else:
        form = LoginForm()

    return render(request, "auth_tabs.html", {"form": form})


# --- LOGOUT ---
def logout_view(request):
    request.session.flush()
    messages.success(request, "Bạn đã đăng xuất.")
    return redirect("login")


# --- Tải VCF ---
def _fold(line, limit=75):
    if len(line) <= limit:
        return line
    return "\r\n ".join(line[i : i + limit] for i in range(0, len(line), limit))


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

    # Social/app chat
    if profile.youtube:
        lines.append(_fold(f"X-SOCIALPROFILE;type=youtube:{profile.youtube}"))
    if profile.zalo:
        lines.append(
            _fold(f"X-SOCIALPROFILE;type=zalo:https://zalo.me/{profile.zalo}")
        )
    if profile.viber:
        lines.append(
            _fold(f"X-SOCIALPROFILE;type=viber:viber://chat?number={profile.viber}")
        )

    # Avatar Cloudinary
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


def template_product(request, id):
    profile = get_object_or_404(Profile, id=id)
    products = profile.products.all()
    return render(request, "product.html", {
        "profile": profile,
        "products": products,
        "current_id": id,
    })


def add_product(request, id):
    profile = get_object_or_404(Profile, id=id)

    # ✅ chỉ cho chính chủ
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

    # ✅ chỉ cho chính chủ
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
    return redirect("edit_profile", id=id)   # 🔥 đổi sang edit_profile
