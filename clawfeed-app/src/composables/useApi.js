/**
 * HTTP request wrapper — works in both H5 and WeChat Mini-Program.
 * In dev: proxied to localhost:8000 via vite proxy.
 * In prod: points to your server domain.
 */

const BASE_URL =
  process.env.NODE_ENV === "development"
    ? "" // vite proxy handles /api → localhost:8000
    : "https://your-domain.com";

function getToken() {
  return uni.getStorageSync("token") || "";
}

function request(url, options = {}) {
  const token = getToken();
  return new Promise((resolve, reject) => {
    uni.request({
      url: BASE_URL + url,
      method: options.method || "GET",
      data: options.data,
      header: {
        Authorization: token ? `Bearer ${token}` : "",
        "Content-Type": "application/json",
        ...options.headers,
      },
      success(res) {
        if (res.statusCode === 401) {
          uni.removeStorageSync("token");
          uni.removeStorageSync("user");
          // Optionally redirect to login
        }
        resolve(res.data);
      },
      fail(err) {
        reject(err);
      },
    });
  });
}

export function useApi() {
  return {
    // Auth
    login: (data) => request("/api/auth/login", { method: "POST", data }),
    devLogin: () => request("/api/auth/dev-login", { method: "POST" }),
    getMe: () => request("/api/auth/me"),
    getAuthConfig: () => request("/api/auth/config"),

    // Digests
    getDigests: (params) => {
      const qs = new URLSearchParams(params).toString();
      return request(`/api/digests${qs ? "?" + qs : ""}`);
    },
    getDigest: (id) => request(`/api/digests/${id}`),

    // Marks
    getMarks: (params) => {
      const qs = params ? new URLSearchParams(params).toString() : "";
      return request(`/api/marks${qs ? "?" + qs : ""}`);
    },
    createMark: (data) => request("/api/marks", { method: "POST", data }),
    deleteMark: (id) => request(`/api/marks/${id}`, { method: "DELETE" }),

    // Sources
    getSources: () => request("/api/sources"),
    getSource: (id) => request(`/api/sources/${id}`),
    createSource: (data) => request("/api/sources", { method: "POST", data }),
    updateSource: (id, data) =>
      request(`/api/sources/${id}`, { method: "PUT", data }),
    deleteSource: (id) => request(`/api/sources/${id}`, { method: "DELETE" }),
    resolveSource: (url) =>
      request("/api/sources/resolve", { method: "POST", data: { url } }),

    // Subscriptions
    getSubscriptions: () => request("/api/subscriptions"),
    subscribe: (sourceId) =>
      request("/api/subscriptions", { method: "POST", data: { sourceId } }),
    unsubscribe: (sourceId) =>
      request(`/api/subscriptions/${sourceId}`, { method: "DELETE" }),
    bulkSubscribe: (sourceIds) =>
      request("/api/subscriptions/bulk", { method: "POST", data: { sourceIds } }),

    // Packs
    getPacks: () => request("/api/packs"),
    getPack: (slug) => request(`/api/packs/${slug}`),
    createPack: (data) => request("/api/packs", { method: "POST", data }),
    installPack: (slug) =>
      request(`/api/packs/${slug}/install`, { method: "POST" }),
    deletePack: (id) => request(`/api/packs/${id}`, { method: "DELETE" }),

    // Feedback
    getFeedback: () => request("/api/feedback"),
    createFeedback: (data) =>
      request("/api/feedback", { method: "POST", data }),
    markFeedbackRead: () =>
      request("/api/feedback/read", { method: "POST" }),

    // Config
    getConfig: () => request("/api/config"),
    getChangelog: (lang) => request(`/api/changelog?lang=${lang || "zh"}`),
    getRoadmap: (lang) => request(`/api/roadmap?lang=${lang || "zh"}`),
  };
}
