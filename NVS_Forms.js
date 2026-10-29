/* Shared template lookup. No file storage, uploads, Drive permission changes or unverified catalog reads.
 * A verified server adapter is not yet supplied. Production state therefore remains pending/empty.
 */
(() => {
  "use strict";
  const normalize = (value) =>
    String(value || "")
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .replace(/đ/g, "d")
      .replace(/Đ/g, "D")
      .toLowerCase()
      .replace(/[._-]+/g, " ")
      .replace(/\s+/g, " ")
      .trim();
  function validRecord(record) {
    if (
      !record ||
      record.approvalStatus !== "approved" ||
      record.active !== true ||
      record.canDownload !== true
    )
      return false;
    for (const field of [
      "code",
      "name",
      "module",
      "fileType",
      "fileId",
      "url",
      "version",
      "accessScope",
      "fileName",
    ])
      if (typeof record[field] !== "string" || !record[field].trim())
        return false;
    if (
      !/^[A-Z0-9]+(?:-[A-Z0-9]+)+$/.test(record.code) ||
      !/^[-\w]+$/.test(record.fileId)
    )
      return false;
    if (!record.fileName.startsWith(record.code)) return false;
    for (const key of ["aliases", "keywords"])
      if (
        record[key] !== undefined &&
        (!Array.isArray(record[key]) ||
          record[key].some((value) => typeof value !== "string"))
      )
        return false;
    for (const [key, direction] of [
      ["effectiveFrom", "from"],
      ["effectiveTo", "to"],
    ])
      if (record[key]) {
        const time = Date.parse(record[key]);
        if (
          !Number.isFinite(time) ||
          (direction === "from" ? time > Date.now() : time <= Date.now())
        )
          return false;
      }
    try {
      const url = new URL(record.url);
      if (
        url.protocol !== "https:" ||
        !["drive.google.com", "docs.google.com"].includes(url.hostname) ||
        url.username ||
        url.password
      )
        return false;
      const id =
        url.pathname.match(
          /\/(?:file\/d|document\/d|spreadsheets\/d|presentation\/d)\/([-\w]+)/,
        )?.[1] || url.searchParams.get("id");
      if (id !== record.fileId) return false;
    } catch (_) {
      return false;
    }
    return true;
  }
  /* Defensive presentation checks; real ACL filtering must occur at the server before records arrive. */
  function filterVerifiedResponse(response, context) {
    if (
      !context ||
      context.verifiedByApprovedAdapter !== true ||
      !context.subject ||
      response?.subject !== context.subject ||
      !Array.isArray(response.items)
    )
      return [];
    const counts = new Map();
    for (const item of response.items)
      counts.set(item?.code, (counts.get(item?.code) || 0) + 1);
    return response.items.filter(
      (record) => validRecord(record) && counts.get(record.code) === 1,
    );
  }
  function search(items, query = "", filters = {}) {
    const terms = normalize(query).split(" ").filter(Boolean);
    return items.filter(
      (record) =>
        validRecord(record) &&
        (!filters.module ||
          (filters.module === "OTHER"
            ? !/^A\.[1-6](?:\.|$)/.test(record.module)
            : record.module === filters.module ||
              record.module.startsWith(filters.module + "."))) &&
        (!filters.fileType ||
          normalize(record.fileType) === normalize(filters.fileType)) &&
        (!filters.documentType ||
          record.documentType === filters.documentType) &&
        terms.every((term) =>
          normalize(
            [
              record.code,
              record.name,
              record.description,
              record.subject,
              ...(record.aliases || []),
              ...(record.keywords || []),
            ].join(" "),
          ).includes(term),
        ),
    );
  }
  const state = Object.freeze({
    status: "pending",
    items: Object.freeze([]),
    message:
      "Chờ kết nối danh mục biểu mẫu và xác minh quyền truy cập. Chưa có kết quả tra cứu.",
  });
  function getByCode() {
    return null;
  }
  window.NVSForms = Object.freeze({
    normalize,
    validRecord,
    filterVerifiedResponse,
    search,
    getState: () => state,
    getByCode,
  });
})();
