/* A.1: distinct report/link/catalog flows. Existing session/personnel/assistant are reused.
 * No new write API, meeting action, signatures, student records or simulated send success.
 */
(() => {
  "use strict";
  const $ = (id) => document.getElementById(id),
    params = new URL(location.href).searchParams;
  let group = ["A11", "A12", "A13", "A14"].includes(params.get("group"))
    ? params.get("group")
    : null;
  const aliases = {
    team: ["A13", "team"],
    cluster: ["A13", "cluster"],
    gifted: ["A14", "hsg"],
    support: ["A14", "support"],
    exam: ["A14", "exam"],
  };
  let data = null,
    sources = null,
    current = null,
    actorUsername = "",
    dirty = false,
    people = new Map(),
    selected = new Set(),
    loading = false;
  function element(tag, text) {
    const n = document.createElement(tag);
    if (text !== undefined) n.textContent = text;
    return n;
  }
  function message(text, error = false) {
    $("notice").textContent = text;
    $("notice").dataset.error = String(error);
  }
  function read(key) {
    for (const kind of ["localStorage", "sessionStorage"]) {
      try {
        const value = window[kind].getItem(key);
        if (value) return value;
      } catch (_) {}
    }
    return "";
  }
  function identity() {
    let user = {};
    try {
      user = JSON.parse(read("user") || "{}") || {};
    } catch (_) {}
    const username = String(
        user.tenDangNhap || user.username || user.userName || "",
      ).trim(),
      expires = Number(read("hvaSessionExpiresAt"));
    if (
      !username ||
      !read("hvaSessionToken") ||
      !Number.isFinite(expires) ||
      expires <= Date.now()
    )
      throw Error("Vui lòng về Trang chủ đăng nhập trước khi chuẩn bị hồ sơ.");
    if (actorUsername && username.toLowerCase() !== actorUsername.toLowerCase())
      throw Error(
        "Tài khoản đã thay đổi. Vui lòng tải lại trang trước khi tiếp tục.",
      );
    return {
      username,
      name: String(user.hoTen || user.fullName || username),
      unit: String(user.toBoPhan || user.tenTo || user.to || "Chưa xác định"),
      role: String(
        user.chucVu || user.viTriViecLam || user.role || "Chưa xác định",
      ),
    };
  }
  function requireIdentity() {
    try {
      return identity();
    } catch (error) {
      const fields = $("formFields");
      if (fields) fields.disabled = true;
      const view = $("previewCard");
      if (view) view.hidden = true;
      $("loginLink")?.removeAttribute("hidden");
      throw error;
    }
  }
  function operationUrl(id) {
    const op = data.operations[id];
    return (
      "./NVS_BaoCao_A1.html?view=a1-20261029&group=" +
      op.group +
      "&item=" +
      encodeURIComponent(id)
    );
  }
  function driveUrl(value) {
    if (!value) return true;
    try {
      const url = new URL(value);
      return (
        url.protocol === "https:" &&
        ["drive.google.com", "docs.google.com"].includes(url.hostname) &&
        !url.username &&
        !url.password &&
        /^\/(file\/d\/|drive\/folders\/|document\/d\/|spreadsheets\/d\/|presentation\/d\/)[A-Za-z0-9_-]+(?:\/|$)/.test(
          url.pathname,
        )
      );
    } catch (_) {
      return false;
    }
  }
  function approvedTemplate(op) {
    const code = sources.templateCodes?.[op.template];
    return code ? window.NVSForms?.getByCode(code) : null;
  }
  function helperButton(label) {
    const button = element("button", label);
    button.type = "button";
    button.className = "btn secondary";
    button.dataset.nvsNav = "ai";
    return button;
  }
  function status(op) {
    return op.kind === "legacy" ? op.statusLabel || "Nghiệp vụ hiện hành" : "Đang phát triển";
  }
  function catalog(sectionId) {
    $("heading").textContent = data.groups[group].name;
    $("description").textContent =
      "Chọn đúng nghiệp vụ để mở biểu mẫu hoặc nộp liên kết tài liệu.";
    $("operation").hidden = true;
    $("catalog").hidden = false;
    $("backToGroup").href = "./NghiepVu.html";
    $("backToGroup").textContent = "Danh mục Nghiệp vụ số";
    for (const section of data.groups[group].sections) {
      const card = element("section");
      card.className = "card a1-catalog-section";
      card.dataset.section = section.id;
      card.append(element("h2", section.name));
      const grid = element("div");
      grid.className = "a1-catalog-grid";
      for (const op of Object.values(data.operations).filter(
        (op) => op.group === group && op.section === section.id,
      )) {
        const link = element("a");
        link.className = "a1-operation-card";
        link.href = op.kind === "legacy" ? op.url : operationUrl(op.id);
        link.dataset.operation = op.id;
        link.append(element("strong", op.name), element("span", status(op)));
        if (op.kind === "link")
          link.append(element("small", "Nộp liên kết Google Drive"));
        else if (op.kind === "report")
          link.append(element("small", "Lập báo cáo và xem trước"));
        else if (op.reason) link.append(element("small", op.reason));
        grid.append(link);
      }
      card.append(grid);
      $("catalog").append(card);
    }
    if (sectionId)
      $("catalog")
        .querySelector('[data-section="' + sectionId + '"]')
        ?.scrollIntoView({ block: "start" });
    message(
      "Các mục ghi Đang phát triển chưa mở lưu hoặc gửi hồ sơ. Nghiệp vụ hiện hành giữ nguyên.",
    );
  }
  function renderBlocked(op) {
    const card = element("section");
    card.className = "card";
    card.append(element("h2", "Đang phát triển"), element("p", op.reason));
    if (op.plannedAreas) {
      card.append(element("h3", "Cấu trúc chuẩn bị — chưa mở dữ liệu"));
      const areas = element("ul");
      op.plannedAreas.forEach((name) => areas.append(element("li", name)));
      card.append(areas);
    }
    if (op.workflow) {
      card.append(element("h3", "Quy trình dự kiến cần được phê duyệt"));
      const list = element("ol");
      op.workflow.forEach((text) => list.append(element("li", text)));
      card.append(list);
      card.append(
        element(
          "p",
          "Các trạng thái dự kiến: " +
            op.statuses.join(" · ") +
            ". Đây không phải trạng thái của hồ sơ đã gửi. Phê duyệt thuộc không gian Điều hành, không thực hiện trong nhóm A.",
        ),
      );
    }
    if (op.kind === "external") {
      const url = sources[op.configKey];
      if (
        url &&
        /^https:\/\/script\.google\.com\/macros\/s\/[A-Za-z0-9_-]+\/exec$/.test(
          url,
        )
      ) {
        const link = element("a", "Mở Sổ ghi đầu bài BD HSG 12");
        link.className = "btn primary";
        link.href = url;
        link.target = "_blank";
        link.rel = "noopener noreferrer";
        card.append(link);
      } else {
        const button = element(
          "button",
          "Chờ liên kết Sổ ghi đầu bài BD HSG 12",
        );
        button.type = "button";
        button.disabled = true;
        button.className = "btn secondary";
        card.append(button);
      }
    }
    $("operation").append(card);
    message(
      op.kind === "external"
        ? "Chỉ tích hợp đường dẫn sổ hiện hành khi được cung cấp; không sửa sổ hoặc dữ liệu."
        : op.reason,
    );
  }
  function recipients() {
    const box = element("section");
    box.className = "a1-recipients";
    box.append(
      element("strong", "Nơi tiếp nhận: Ban Giám hiệu Trường THPT Hòa Vang"),
      element(
        "p",
        "Tổ trưởng phụ trách nhận thông tin theo phân công và quyền được duyệt. Người gửi không tự sửa người nhận bắt buộc.",
      ),
      element(
        "p",
        "Đang phát triển — chờ xác định người nhận và quyền. Việc hiển thị ở đây không đồng nghĩa hồ sơ đã được gửi.",
      ),
    );
    return box;
  }
  function templatePanel(op) {
    if (!op.template) return null;
    const section = element("section");
    section.className = "a1-template";
    const template = approvedTemplate(op),
      code = sources.templateCodes?.[op.template];
    section.append(element("h3", "Mẫu tài liệu"));
    const lookup = element("a", "Tra cứu biểu mẫu được phép sử dụng");
    lookup.className = "btn secondary";
    lookup.href =
      "./NVS_BieuMau.html" + (code ? "?code=" + encodeURIComponent(code) : "");
    section.append(lookup);
    if (template) {
      const link = element("a", "Tải mẫu " + (template.code || code || ""));
      link.className = "btn secondary";
      link.href = template.url;
      link.target = "_blank";
      link.rel = "noopener noreferrer";
      section.append(
        link,
        element(
          "p",
          "Sử dụng đúng nội dung và phiên bản được nhà trường duyệt.",
        ),
      );
    } else {
      const button = element(
        "button",
        "Tải mẫu — chờ nguồn được duyệt và quyền truy cập",
      );
      button.type = "button";
      button.className = "btn secondary";
      button.disabled = true;
      button.dataset.templateDownload = "";
      section.append(
        button,
        element(
          "p",
          "Chưa có nguồn mẫu đã duyệt và quyền được xác minh. Không công bố mẫu dự thảo hoặc tạo mẫu thay thế.",
        ),
      );
    }
    return section;
  }
  function renderIdentity(op) {
    const card = element("div");
    card.className = "identity-card";
    const actor = element("div");
    actor.className = "identity-col";
    actor.append(element("div", "NGƯỜI BÁO CÁO / NỘP HỒ SƠ"));
    const name = element("div");
    name.id = "identityName";
    name.className = "identity-name";
    const info = element("div");
    info.className = "identity-meta";
    for (const [id, label] of [
      ["identityTeam", "Tổ / bộ phận"],
      ["identityRole", "Chức vụ"],
    ]) {
      const p = element("p", label + ": "),
        value = element("b");
      value.id = id;
      p.append(value);
      info.append(p);
    }
    actor.append(name, info);
    card.append(actor);
    const verified = element("div");
    verified.className = "identity-col";
    verified.append(element("strong", "THÔNG TIN NHÂN SỰ"));
    const text = element(
      "p",
      "Thông tin phiên đăng nhập; chưa đối chiếu để gửi.",
    );
    text.id = "identityStatus";
    const load = element("button", "Đối chiếu nhân sự HVA");
    load.className = "btn secondary";
    load.type = "button";
    load.dataset.loadIdentity = "";
    load.onclick = () => loadPersonnel();
    verified.append(text, load);
    card.append(verified);
    const signing = element("div");
    signing.className = "identity-col";
    signing.append(
      element("strong", "XÁC NHẬN HỒ SƠ"),
      element(
        "p",
        "Đang phát triển — chưa mở xác nhận và gửi cho biểu mẫu này.",
      ),
    );
    card.append(signing);
    return card;
  }
  function updateIdentity(person) {
    $("identityName").textContent = person.name;
    $("identityTeam").textContent = person.unit;
    $("identityRole").textContent = person.role;
  }
  function renderPeople() {
    const list = $("peopleList");
    if (!list) return;
    const keyword = ($("peopleSearch")?.value || "")
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .toLowerCase()
      .replace(/đ/g, "d");
    list.replaceChildren();
    for (const [id, person] of people) {
      if (
        keyword &&
        !(person.name + " " + person.unit)
          .normalize("NFD")
          .replace(/[\u0300-\u036f]/g, "")
          .toLowerCase()
          .replace(/đ/g, "d")
          .includes(keyword)
      )
        continue;
      const wrap = element("label");
      wrap.className = "a1-person-option";
      const input = element("input");
      input.type = "checkbox";
      input.checked = selected.has(id);
      input.dataset.person = id;
      if (current?.people === "colleagues" && !person.isTeacher)
        input.disabled = true;
      input.onchange = () => {
        try {
          requireIdentity();
          if (input.checked) selected.add(id);
          else selected.delete(id);
          dirty = true;
          renderPeople();
          hidePreview();
        } catch (error) {
          message(error.message, true);
        }
      };
      wrap.append(
        input,
        element(
          "span",
          person.name +
            " · " +
            person.unit +
            (current?.people === "colleagues" && !person.isTeacher
              ? " · Chưa xác nhận vai trò giảng dạy"
              : ""),
        ),
      );
      list.append(wrap);
    }
    if (!list.childNodes.length)
      list.append(
        element(
          "p",
          people.size
            ? "Không có nhân sự phù hợp trong danh sách đã tải."
            : "Chưa tải danh sách nhân sự HVA; không sử dụng danh sách mẫu.",
        ),
      );
    $("peopleCount").textContent =
      "Đã chọn " + selected.size + " người từ danh sách nhận được.";
  }
  async function loadPersonnel() {
    if (loading) return;
    let account;
    try {
      account = requireIdentity();
    } catch (error) {
      message(error.message, true);
      return;
    }
    loading = true;
    const controls = [
      ...document.querySelectorAll("[data-load-identity],[data-load-people]"),
    ];
    controls.forEach((n) => (n.disabled = true));
    message("Đang đối chiếu nhân sự HVA…");
    try {
      const groups = await window.HVAPersonnel.buildGroups();
      requireIdentity();
      people = new Map();
      for (const group of groups || [])
        for (const raw of group.members || []) {
          const original =
              raw.raw && typeof raw.raw === "object" ? raw.raw : raw,
            p = window.HVAPersonnel.normalize(raw, group.tenTo || ""),
            username = String(p.username || "").trim();
          if (!username) continue;
          const id = username.toLowerCase();
          if (!people.has(id))
            people.set(id, {
              username,
              name: String(p.hoTen || username),
              unit: String(
                original.toBoPhan ||
                  original.to ||
                  original.tenTo ||
                  "Chưa xác định",
              ),
              role: String(
                original.chucVu ||
                  original.viTriViecLam ||
                  original.vaiTro ||
                  "Chưa xác định",
              ),
              isTeacher: [
                original.chucVu,
                original.viTriViecLam,
                original.vaiTro,
              ].some((value) =>
                /^(giao vien(?:\s|$)|gv$)/.test(
                  String(value || "")
                    .normalize("NFD")
                    .replace(/[\u0300-\u036f]/g, "")
                    .toLowerCase()
                    .trim(),
                ),
              ),
            });
        }
      for (const id of [...selected]) if (!people.has(id)) selected.delete(id);
      const self = people.get(account.username.toLowerCase());
      if (self) {
        updateIdentity(self);
        $("identityStatus").textContent =
          self.unit === "Chưa xác định" || self.role === "Chưa xác định"
            ? "Nguồn đã trả tài khoản nhưng còn thiếu tổ / chức vụ; không tự bổ sung. Chưa đủ điều kiện gửi."
            : "Đã đối chiếu thông tin với nguồn nhân sự HVA. Chức năng xác nhận và gửi chưa mở.";
      } else {
        $("identityStatus").textContent =
          "Nguồn chưa xác định được tài khoản hiện tại; chưa đủ điều kiện xác nhận và gửi.";
      }
      renderPeople();
      hidePreview();
      message(
        people.size
          ? "Đã nhận danh sách theo nguồn HVA hiện có; chưa lưu hoặc gửi hồ sơ."
          : "Nguồn chưa trả danh sách nhân sự sử dụng được. Không thay bằng dữ liệu mẫu.",
        !people.size,
      );
    } catch (_) {
      people.clear();
      selected.clear();
      renderPeople();
      $("identityStatus").textContent =
        "Chưa đối chiếu được nhân sự. Có thể tải lại sau khi kiểm tra đăng nhập.";
      message(
        "Chưa tải được nhân sự HVA. Không tự gán tổ, chức vụ hoặc thay bằng danh sách mẫu.",
        true,
      );
    } finally {
      loading = false;
      controls.forEach((n) => (n.disabled = false));
    }
  }
  function hidePreview() {
    const preview = $("previewCard");
    if (preview) preview.hidden = true;
    $("s2")?.classList.remove("on");
  }
  function addField(parent, spec) {
    const wrap = element("div");
    wrap.className = "field" + (spec.kind === "textarea" ? " full" : "");
    const label = element("label", spec.label);
    label.htmlFor = "field-" + spec.key;
    if (spec.required) label.append(element("b", " *"));
    const input = element(spec.kind === "textarea" ? "textarea" : "input");
    input.id = "field-" + spec.key;
    input.dataset.field = spec.key;
    input.required = spec.required;
    input.maxLength = spec.kind === "textarea" ? 10000 : 1000;
    if (spec.kind !== "textarea") input.type = spec.kind;
    if (spec.kind === "number") {
      input.min = "0";
      input.step = "1";
    }
    if (spec.key === "year") {
      input.value = "2026–2027";
      input.title = "Nhập năm học theo dạng 2026–2027";
    }
    wrap.append(label, input);
    parent.append(wrap);
  }
  function peoplePanel(op) {
    const section = element("section");
    section.className = "a1-personnel";
    section.append(
      element(
        "h3",
        op.people === "colleagues"
          ? "Giáo viên cùng phụ trách"
          : "Thành phần tham gia",
      ),
    );
    const load = element("button", "Tải nhân sự HVA");
    load.type = "button";
    load.className = "btn secondary";
    load.dataset.loadPeople = "";
    load.onclick = () => loadPersonnel();
    section.append(load);
    const label = element("label", "Tìm người trong danh sách đã tải"),
      search = element("input");
    search.type = "search";
    search.id = "peopleSearch";
    search.oninput = renderPeople;
    label.append(search);
    const list = element("div");
    list.id = "peopleList";
    const count = element("p");
    count.id = "peopleCount";
    section.append(
      label,
      list,
      count,
      element(
        "p",
        "Không nhập tên học sinh hoặc tự tạo nhân sự. Lựa chọn chỉ dùng trong bản xem trước; vai trò giảng dạy cần có căn cứ từ dữ liệu nhân sự.",
      ),
    );
    return section;
  }
  function renderPreviewShell(op) {
    const section = element("section");
    section.id = "previewCard";
    section.className = "card preview-shell";
    section.hidden = true;
    const toolbar = element("div");
    toolbar.className = "preview-toolbar";
    toolbar.append(
      element(
        "b",
        op.kind === "report" ? "BẢN XEM TRƯỚC BÁO CÁO" : "THÔNG TIN NỘP HỒ SƠ",
      ),
    );
    const edit = element("button", "Quay lại chỉnh sửa");
    edit.type = "button";
    edit.className = "btn secondary";
    edit.id = "edit";
    edit.onclick = () => {
      hidePreview();
      $("declareCard").scrollIntoView({ behavior: "smooth" });
    };
    toolbar.append(edit);
    section.append(toolbar);
    const view = element("div");
    view.className =
      op.kind === "report" ? "paper-scroll-wrapper" : "a1-link-preview";
    const paper = element("article");
    paper.id = "previewPaper";
    if (op.kind === "report") paper.className = "official-paper";
    view.append(paper);
    section.append(view);
    const actions = element("div");
    actions.className = "actions";
    for (const label of ["Xác nhận / ký", "Xác nhận và gửi BGH"]) {
      const b = element("button", label + " — Đang phát triển");
      b.type = "button";
      b.className = "btn secondary";
      b.disabled = true;
      actions.append(b);
    }
    section.append(actions);
    return section;
  }
  function renderForm(op) {
    const workspace = $("operation"),
      steps = element("div");
    steps.className = "steps";
    for (const [i, text] of [
      "Chuẩn bị nội dung",
      "Xem trước",
      "Xác nhận và gửi",
    ].entries()) {
      const step = element("div");
      step.className = "step" + (!i ? " on" : "");
      step.id = "s" + (i + 1);
      step.append(
        element("span", String(i + 1)),
        document.createTextNode(text),
      );
      steps.append(step);
    }
    workspace.append(steps);
    const pending = element(
      "p",
      op.kind === "link"
        ? "Đang phát triển — có thể chuẩn bị thông tin và liên kết, chưa mở nộp hồ sơ. Không nhập lại nội dung đã có trong tài liệu."
        : "Đang phát triển — có thể lập nội dung và xem trước, chưa mở lưu, ký hoặc gửi báo cáo.",
    );
    pending.className = "a1-development";
    workspace.append(pending);
    const template = templatePanel(op);
    if (template) workspace.append(template);
    const card = element("section");
    card.id = "declareCard";
    card.className = "card";
    card.append(renderIdentity(op));
    const form = element("form");
    form.id = "reportForm";
    form.noValidate = true; // Verify session first; reportValidity below still validates required fields.
    const fields = element("fieldset");
    fields.id = "formFields";
    fields.disabled = true;
    const grid = element("div");
    grid.className = "grid";
    for (const spec of op.fields) addField(grid, spec);
    if (op.kind === "link")
      addField(grid, {
        key: "note",
        label: "Ghi chú (không bắt buộc)",
        kind: "text",
        required: false,
      });
    const drive = {
      key: "drive",
      label:
        op.kind === "link"
          ? "Liên kết tài liệu Google Drive / Docs"
          : "Liên kết tài liệu, minh chứng (nếu có)",
      kind: "url",
      required: op.kind === "link",
    };
    addField(grid, drive);
    fields.append(grid);
    const feedback = element(
      "p",
      "Chỉ kiểm tra định dạng liên kết; quyền truy cập tài liệu chưa được kiểm chứng.",
    );
    feedback.id = "driveStatus";
    fields.append(feedback);
    if (op.people) fields.append(peoplePanel(op));
    const actions = element("div");
    actions.className = "actions";
    const preview = element(
      "button",
      op.kind === "report" ? "Xem bản báo cáo A4" : "Xem trước thông tin nộp",
    );
    preview.type = "submit";
    preview.id = "preview";
    preview.className = "btn primary";
    const assistant = helperButton(
      op.kind === "report" ? "Trợ lý soạn báo cáo" : "Trợ lý NVS",
    );
    const reset = element("button", "Làm mới");
    reset.type = "button";
    reset.className = "btn secondary";
    reset.id = "reset";
    reset.onclick = () => {
      try {
        requireIdentity();
        if (dirty && !confirm("Xóa nội dung chưa được lưu của biểu mẫu này?"))
          return;
        form.reset();
        selected.clear();
        renderPeople();
        hidePreview();
        dirty = false;
        message("Đã làm mới nội dung trên trang; không thay đổi dữ liệu thật.");
      } catch (error) {
        message(error.message, true);
      }
    };
    actions.append(preview, assistant, reset);
    for (const label of ["Lưu nháp", "Xác nhận / ký", "Gửi"]) {
      const button = element("button", label + " — Đang phát triển");
      button.type = "button";
      button.disabled = true;
      button.className = "btn secondary";
      actions.append(button);
    }
    fields.append(actions);
    form.append(fields);
    form.onsubmit = (event) => {
      event.preventDefault();
      try {
        previewReport();
      } catch (error) {
        message(error.message, true);
      }
    };
    form.oninput = () => {
      dirty = true;
      hidePreview();
    };
    card.append(form, recipients());
    const login = element("p");
    login.id = "loginLink";
    login.hidden = true;
    const link = element("a", "Về Trang chủ để đăng nhập");
    link.href = "./index.html";
    login.append(link);
    card.append(login);
    workspace.append(card, renderPreviewShell(op));
    const history = element("section");
    history.className = "card";
    history.append(
      element("h2", "Lịch sử và phản hồi"),
      element(
        "p",
        "Đang phát triển — chỉ hiển thị hồ sơ, trạng thái tiếp nhận và phản hồi khi có nguồn dữ liệu và quyền được xác nhận.",
      ),
    );
    workspace.append(history);
    if (op.group === "A13") {
      const rights = element("section");
      rights.className = "card";
      rights.append(element("h2", "Vai trò trong sinh hoạt chuyên môn"));
      for (const role of [
        "Giáo viên",
        "Người được giao chủ trì",
        "Tổ trưởng chuyên môn",
        "Ban Giám hiệu",
      ])
        rights.append(
          element(
            "p",
            role +
              ": chờ quy tắc quyền được nhà trường xác nhận cho nghiệp vụ này.",
          ),
        );
      rights.append(
        element(
          "p",
          "Không suy quyền chủ trì từ chức vụ; chưa mở quyền nộp, đọc hoặc xử lý hồ sơ thật.",
        ),
      );
      workspace.append(rights);
    }
    try {
      const account = identity();
      actorUsername = account.username;
      updateIdentity(account);
      fields.disabled = false;
      message(
        "Có thể chuẩn bị nội dung theo tài khoản hiện tại. Chưa lưu hoặc gửi; không nhập thông tin học sinh nhạy cảm.",
      );
    } catch (error) {
      login.hidden = false;
      message(error.message, true);
    }
    if (op.people) renderPeople();
    const urlInput = $("field-drive");
    urlInput.oninput = () => {
      $("driveStatus").textContent = !urlInput.value.trim()
        ? "Chưa có liên kết."
        : driveUrl(urlInput.value.trim())
          ? "Đúng định dạng liên kết. Chưa kiểm chứng quyền truy cập tài liệu."
          : "Liên kết phải thuộc Google Drive hoặc Google Docs và có định dạng tài liệu hợp lệ.";
    };
  }
  function fieldValues() {
    return Object.fromEntries(
      [...document.querySelectorAll("#reportForm [data-field]")].map(
        (input) => [input.dataset.field, input.value.trim()],
      ),
    );
  }
  function previewReport() {
    const account = requireIdentity(),
      form = $("reportForm");
    if (!form.reportValidity()) return;
    const values = fieldValues();
    if (values.year && !/^\d{4}\s*(?:-|–|\/)\s*\d{4}$/.test(values.year))
      throw Error("Năm học cần theo dạng 2026–2027.");
    for (const spec of current.fields) {
      const value = values[spec.key];
      if (spec.required && !value)
        throw Error(spec.label + ": không được để trống.");
      if (spec.kind === "url" && !driveUrl(value))
        throw Error(spec.label + ": cần liên kết Google Drive / Docs hợp lệ.");
      if (
        spec.kind === "number" &&
        value &&
        (!Number.isSafeInteger(Number(value)) || Number(value) < 0)
      )
        throw Error(spec.label + ": cần số nguyên không âm.");
    }
    if (values.from && values.to && values.to < values.from)
      throw Error("Ngày kết thúc không được trước ngày bắt đầu.");
    if (!driveUrl(values.drive))
      throw Error("Cần liên kết Google Drive / Docs hợp lệ.");
    if (current.kind === "participants" && !selected.size)
      throw Error("Vui lòng tải nhân sự HVA và chọn người tham gia.");
    const paper = $("previewPaper");
    paper.replaceChildren();
    if (current.kind === "report") {
      const head = element("div");
      head.className = "official-head";
      const agency = element("div");
      agency.className = "agency";
      const parent = element("div", "SỞ GIÁO DỤC VÀ ĐÀO TẠO ĐÀ NẴNG");
      parent.className = "agency-parent";
      const unit = element("strong", "TRƯỜNG THPT HÒA VANG");
      unit.className = "agency-unit";
      agency.append(parent, unit);
      const nation = element("div");
      nation.className = "nation";
      const nationalTitle = element(
        "strong",
        "CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM",
      );
      nationalTitle.className = "nation-title";
      const motto = element("div", "Độc lập - Tự do - Hạnh phúc");
      motto.className = "nation-motto";
      nation.append(nationalTitle, motto);
      head.append(agency, nation);
      paper.append(head);
      const title = element("div", "BÁO CÁO");
      title.className = "official-title";
      const subtitle = element("div", current.name);
      subtitle.className = "official-subtitle";
      paper.append(
        title,
        subtitle,
        element("p", "Kính gửi: Ban Giám hiệu Trường THPT Hòa Vang"),
      );
    } else paper.append(element("h2", current.name));
    paper.append(
      element(
        "p",
        "Người báo cáo / nộp hồ sơ: " + $("identityName").textContent,
      ),
      element("p", "Tổ / bộ phận: " + $("identityTeam").textContent),
      element("p", "Chức vụ: " + $("identityRole").textContent),
    );
    for (const spec of current.fields) {
      if (!values[spec.key]) continue;
      const p = element("p");
      p.append(element("strong", spec.label + ": "));
      if (spec.kind === "url") {
        const link = element("a", values[spec.key]);
        link.href = values[spec.key];
        link.target = "_blank";
        link.rel = "noopener noreferrer";
        p.append(link);
      } else p.append(document.createTextNode(values[spec.key]));
      paper.append(p);
    }
    if (selected.size)
      paper.append(
        element(
          "p",
          (current.people === "colleagues"
            ? "Giáo viên cùng phụ trách: "
            : "Thành phần tham gia: ") +
            [...selected]
              .map((id) => people.get(id)?.name || "")
              .filter(Boolean)
              .join(", "),
        ),
      );
    if (values.note) paper.append(element("p", "Ghi chú: " + values.note));
    if (values.drive) {
      const p = element("p", "Tài liệu / minh chứng: "),
        link = element("a", values.drive);
      link.href = values.drive;
      link.target = "_blank";
      link.rel = "noopener noreferrer";
      p.append(link);
      paper.append(p);
    }
    paper.append(
      element(
        "p",
        "Chờ xác định người nhận theo quyền. BẢN XEM TRƯỚC — CHƯA LƯU, CHƯA KÝ, CHƯA GỬI.",
      ),
    );
    if (current.kind === "report") {
      const sign = element("div");
      sign.className = "official-sign";
      sign.append(
        element("div", "NGƯỜI BÁO CÁO"),
        element("p", "Chưa xác nhận / ký"),
        element("strong", $("identityName").textContent),
      );
      paper.append(sign);
    }
    $("previewCard").hidden = false;
    $("s2").classList.add("on");
    $("previewCard").scrollIntoView({ behavior: "smooth" });
    message("Đã mở bản xem trước. Nội dung chưa được lưu, ký hoặc gửi.");
  }
  async function start() {
    try {
      const results = await Promise.all([
        fetch("./NVS_A1.schemas.json", { cache: "no-store" }),
        fetch("./NVS_A1.sources.json", { cache: "no-store" }),
      ]);
      if (results.some((response) => !response.ok))
        throw Error("Chưa tải được danh mục A.1. Vui lòng tải lại trang.");
      [data, sources] = await Promise.all(
        results.map((response) => response.json()),
      );
      const requestedId = params.get("item") || params.get("type");
      const requested = data.operationAliases?.[requestedId] ||
        (data.operations[requestedId] ? requestedId : null);
      group ||= data.operations[requested]?.group || aliases[requestedId]?.[0] || "A11";
      if (params.get("item") && !requested)
        throw Error("Không tìm thấy nghiệp vụ. Vui lòng chọn lại từ danh mục A.1.");
      if (!requested) {
        catalog(aliases[params.get("type")]?.[1]);
        return;
      }
      const op = data.operations[requested];
      if (!op || op.group !== group)
        throw Error(
          "Không tìm thấy nghiệp vụ trong nhóm này. Vui lòng chọn lại từ danh mục A.1.",
        );
      current = op;
      $("heading").textContent = op.name;
      document.title = op.name + " | THPT Hòa Vang";
      $("description").textContent =
        op.description ||
        (op.kind === "link"
          ? "Chuẩn bị theo mẫu được duyệt và nộp bằng liên kết Google Drive."
          : "Lập nội dung theo đúng nghiệp vụ; kiểm tra trước khi xác nhận.");
      $("backToGroup").href =
        "./NVS_BaoCao_A1.html?view=a1-20261029&group=" + group;
      $("backToGroup").textContent = "← " + data.groups[group].name;
      $("catalog").hidden = true;
      $("operation").hidden = false;
      if (op.kind === "legacy") {
        const link = element("a", "Mở " + op.name);
        link.href = op.url;
        link.className = "btn primary";
        $("operation").append(link);
        message(
          "Giữ nguyên nghiệp vụ hiện hành và dữ liệu; không tạo biểu mẫu thay thế.",
        );
        return;
      }
      if (["blocked", "external"].includes(op.kind)) {
        renderBlocked(op);
        return;
      }
      renderForm(op);
    } catch (error) {
      message(error.message, true);
    }
  }
  window.addEventListener("beforeunload", (event) => {
    if (!dirty) return;
    event.preventDefault();
    event.returnValue = "";
  });
  document.addEventListener("click", (event) => {
    const button = event.target.closest(
      "[data-nvs-nav=calendar],[data-nvs-nav=person],[data-nvs-nav=connect]",
    );
    if (!button) return;
    event.preventDefault();
    if (button.dataset.nvsNav === "connect") {
      message("Chức năng Kết nối đang phát triển.");
      return;
    }
    location.assign(
      "./NVS_TraCuu.html?item=" +
        (button.dataset.nvsNav === "calendar" ? "B.1.2" : "C.1"),
    );
  });
  start();
})();
