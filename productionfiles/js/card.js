// ================== DETECT MOBILE ==================
function isMobileUA() {
  const ua = navigator.userAgent || navigator.vendor || window.opera;
  return /Android|iPhone|iPad|iPod/i.test(ua);
}

// ================== CHUẨN HÓA SỐ ==================
function normalizePhone(raw) {
  if (!raw) return "";
  const t = String(raw).trim();
  const keepPlus = t.startsWith("+");
  const digits = t.replace(/\D/g, "");
  return keepPlus ? "+" + digits : digits;
}

// ================== LƯU DANH BẠ ==================
(function attachSaveHandler() {
  const btn = document.getElementById("saveContact");
  if (!btn) return;
  btn.addEventListener("click", function (e) {
    const phoneRaw = btn.getAttribute("data-phone") || "";
    const phone = normalizePhone(phoneRaw);
    if (isMobileUA() && phone) {
      e.preventDefault();
      window.location.href = "tel:" + phone;
    }
  });
})();

// ================== URL PROFILE ==================
const PROFILE_URL = "{{ request.build_absolute_uri|escapejs }}";

// ================== CHIA SẺ ==================
(function sharePopupHandlers() {
  const btnDownloadQR = document.getElementById("btnDownloadQR");
  const btnCopyLink = document.getElementById("btnCopyLink");
  const btnShare = document.getElementById("btnShare");
  const qrImg = document.getElementById("qrImage");

  // 1) TẢI ẢNH QR
  if (btnDownloadQR && qrImg) {
    btnDownloadQR.addEventListener("click", async () => {
      try {
        const res = await fetch(qrImg.src, { cache: "no-store" });
        const blob = await res.blob();
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = "qr_profile_{{ profile.id }}.png";
        document.body.appendChild(a);
        a.click();
        a.remove();
        URL.revokeObjectURL(url);
      } catch (e) {
        alert("Không thể tải ảnh QR. Vui lòng thử lại.");
      }
    });
  }

  // 2) COPY LINK PROFILE
  if (btnCopyLink) {
    btnCopyLink.addEventListener("click", async () => {
      try {
        await navigator.clipboard.writeText(PROFILE_URL);
        alert("Đã copy link: " + PROFILE_URL);
      } catch (e) {
        const ta = document.createElement("textarea");
        ta.value = PROFILE_URL;
        document.body.appendChild(ta);
        ta.select();
        document.execCommand("copy");
        ta.remove();
        alert("Đã copy link: " + PROFILE_URL);
      }
    });
  }

  // 3) CHIA SẺ
  if (btnShare) {
    btnShare.addEventListener("click", async () => {
      const shareData = {
        title: "{{ profile.full_name|escapejs }}",
        text: "Danh thiếp số của {{ profile.full_name|escapejs }}",
        url: PROFILE_URL,
      };

      if (navigator.share) {
        try {
          await navigator.share(shareData);
        } catch (_) {}
      } else {
        const fb =
          "https://www.facebook.com/sharer/sharer.php?u=" +
          encodeURIComponent(PROFILE_URL);
        window.open(fb, "_blank", "noopener,noreferrer,width=680,height=560");
      }
    });
  }
})();

// ================== MODAL ẢNH ==================
document.addEventListener("DOMContentLoaded", function () {
  const modal = document.getElementById("imageModal");
  const modalImg = document.getElementById("modalImage");
  const closeBtn = document.querySelector(".image-modal .close");

  // --- Avatar ---
  const avatar = document.querySelector(".profile-img");
  if (avatar) {
    avatar.addEventListener("click", function (e) {
      e.stopPropagation(); // Ngăn lan sự kiện ra header
      modal.style.display = "block";
      modalImg.src = this.dataset.full || this.src;
    });
  }

  // --- Background ---
  const body = document.body;
  const bgUrl = body.dataset.bg;
  if (bgUrl) {
    const header = document.querySelector(".header");
    header.addEventListener("click", function (e) {
      // Nếu click trúng avatar thì bỏ qua
      if (e.target.classList.contains("profile-img")) return;
      modal.style.display = "block";
      modalImg.src = bgUrl;
    });
  }

  // --- Đóng modal ---
  if (closeBtn) closeBtn.onclick = () => (modal.style.display = "none");
  modal.onclick = (e) => {
    if (e.target === modal) modal.style.display = "none";
  };
});
