function isMobileUA() {
  const ua = navigator.userAgent || navigator.vendor || window.opera;
  return /Android|iPhone|iPad|iPod/i.test(ua);
}

// Chuẩn hóa số: giữ dấu + đầu và chữ số
function normalizePhone(raw) {
  if (!raw) return "";
  const t = String(raw).trim();
  const keepPlus = t.startsWith("+");
  const digits = t.replace(/\D/g, "");
  return keepPlus ? "+" + digits : digits;
}

// --- LƯU DANH BẠ: mobile + có số => mở app gọi; còn lại để tải .vcf ---
(function attachSaveHandler() {
  const btn = document.getElementById("saveContact");
  if (!btn) return;
  btn.addEventListener("click", function (e) {
    const phoneRaw = btn.getAttribute("data-phone") || "";
    const phone = normalizePhone(phoneRaw);
    if (isMobileUA() && phone) {
      e.preventDefault(); // chặn tải .vcf, ưu tiên gọi
      window.location.href = "tel:" + phone;
    }
  });
})();

// URL chi tiết profile hiện tại (server render từ Django template)
const PROFILE_URL = "{{ request.build_absolute_uri|escapejs }}";

// --- CHIA SẺ: 3 nút trong popup ---
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
        // Fallback nếu clipboard bị chặn
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
        } catch (_) {
          // người dùng đóng menu share -> không làm gì
        }
      } else {
        const fb =
          "https://www.facebook.com/sharer/sharer.php?u=" +
          encodeURIComponent(PROFILE_URL);
        window.open(fb, "_blank", "noopener,noreferrer,width=680,height=560");
      }
    });
  }
})();

document.addEventListener("DOMContentLoaded", function () {
  const modal = document.getElementById("imageModal");
  const modalImg = document.getElementById("modalImage");
  const closeBtn = document.querySelector(".image-modal .close");

  // Avatar
  const avatar = document.querySelector(".profile-img");
  if (avatar) {
    avatar.style.cursor = "zoom-in";
    avatar.addEventListener("click", function () {
      modal.style.display = "block";
      modalImg.src = this.dataset.full || this.src;
    });
  }

  // Background (từ data-bg ở <body>)
  const body = document.body;
  const bgUrl = body.dataset.bg;
  if (bgUrl) {
    const header = document.querySelector(".header");
    header.style.cursor = "zoom-in";
    header.addEventListener("click", function () {
      modal.style.display = "block";
      modalImg.src = bgUrl;
    });
  }

  // Đóng modal
  closeBtn.onclick = () => (modal.style.display = "none");
  modal.onclick = (e) => {
    if (e.target === modal) modal.style.display = "none";
  };
});
