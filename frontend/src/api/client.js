const API_BASE_URL = window.location.port === '3000' ? '/api/v1' : 'http://127.0.0.1:8000/api/v1';
const HEALTH_URL = window.location.port === '3000' ? '/health' : 'http://127.0.0.1:8000/health';
const ROOT_URL = window.location.port === '3000' ? '' : 'http://127.0.0.1:8000';

export const apiClient = {
  async getHealth() {
    const res = await fetch(HEALTH_URL);
    if (!res.ok) throw new Error(`Health check failed: ${res.statusText}`);
    return res.json();
  },

  async getCapabilities() {
    const res = await fetch(`${API_BASE_URL}/capabilities`);
    if (!res.ok) throw new Error(`Failed to load capabilities: ${res.statusText}`);
    return res.json();
  },

  async getDemoPairs() {
    const res = await fetch(`${API_BASE_URL}/images/demo`);
    if (!res.ok) throw new Error(`Failed to load demo pairs: ${res.statusText}`);
    return res.json();
  },

  async uploadImage(file) {
    const formData = new FormData();
    formData.append('file', file);

    const res = await fetch(`${API_BASE_URL}/images/upload`, {
      method: 'POST',
      body: formData
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail || `Upload failed: ${res.statusText}`);
    }
    return res.json();
  },

  async runPipeline(config) {
    const res = await fetch(`${API_BASE_URL}/pipeline/run`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(config)
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail || `Pipeline run failed: ${res.statusText}`);
    }
    return res.json();
  },

  async runRobustness(config) {
    const res = await fetch(`${API_BASE_URL}/experiments/robustness`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(config)
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail || `Robustness experiment failed: ${res.statusText}`);
    }
    return res.json();
  },

  async getRunResults(runId) {
    const res = await fetch(`${API_BASE_URL}/results/${runId}`);
    if (!res.ok) throw new Error(`Failed to fetch run results: ${res.statusText}`);
    return res.json();
  },

  async getCompare(pairName = 'Pair A: bundled prototype') {
    const res = await fetch(`${ROOT_URL}/api/demo/compare`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ pair_name: pairName })
    });
    if (!res.ok) throw new Error(`Failed to fetch compare data: ${res.statusText}`);
    return res.json();
  },

  async getFailureCase() {
    const res = await fetch(`${ROOT_URL}/api/demo/failure-case`);
    if (!res.ok) throw new Error(`Failed to fetch failure case: ${res.statusText}`);
    return res.json();
  },

  getPreviewUrl(imageId) {
    return `${API_BASE_URL}/images/${imageId}/preview`;
  },

  getArtifactUrl(runId, filename) {
    return `${API_BASE_URL}/results/${runId}/artifact/${filename}`;
  },

  getReportUrl(runId) {
    return `${API_BASE_URL}/results/${runId}/report`;
  }
};
