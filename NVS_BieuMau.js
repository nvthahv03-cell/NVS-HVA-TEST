(() => {
  "use strict";
  const $ = (id) => document.getElementById(id),
    state = window.NVSForms.getState(),
    params = new URL(location.href).searchParams;
  $("templateQuery").value = params.get("code") || params.get("q") || "";
  function render() {
    const query = $("templateQuery").value.trim(),
      filters = {
        module: $("templateModule").value,
        fileType: $("templateFileType").value,
        documentType: $("templateDocumentType").value,
      };
    $("templateResults").replaceChildren();
    if (state.status !== "ready") {
      $("templateStatus").textContent =
        state.message +
        " Chỉ công bố mẫu đã được phê duyệt, còn hiệu lực và phù hợp quyền. Không hiển thị mẫu dự thảo.";
      return;
    }
    const items = window.NVSForms.search(state.items, query, filters);
    for (const record of items) {
      const card = document.createElement("article");
      card.className = "card";
      for (const text of [
        record.name,
        "Mã mẫu: " + record.code,
        record.description || "",
        "Phiên bản biểu mẫu: " + record.version,
      ]) {
        const p = document.createElement("p");
        p.textContent = text;
        card.append(p);
      }
      const link = document.createElement("a");
      link.textContent = "Tải từ Google Drive";
      link.className = "btn primary";
      link.href = record.url;
      link.target = "_blank";
      link.rel = "noopener noreferrer";
      card.append(link);
      $("templateResults").append(card);
    }
    $("templateStatus").textContent = items.length
      ? "Kết quả từ nguồn được phép truy cập."
      : "Không có kết quả phù hợp trong danh mục được phép.";
  }
  $("templateSearch").onsubmit = (event) => {
    event.preventDefault();
    render();
  };
  $("templateSearch").onreset = () => setTimeout(render, 0);
  render();
})();
