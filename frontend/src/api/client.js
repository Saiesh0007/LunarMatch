const API_BASE_URL = 'http://127.0.0.1:8000/api/v1';

export const apiClient = {
  async uploadImage(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    const res = await fetch(`${API_BASE_URL}/images/upload`, {
      method: 'POST',
      body: formData
    });
    
    if (!res.ok) {
      throw new Error(`Upload failed: ${res.statusText}`);
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
      throw new Error(`Pipeline run failed: ${res.statusText}`);
    }
    return res.json();
  },
  
  getPreviewUrl(imageId) {
    return `${API_BASE_URL}/images/${imageId}/preview`;
  }
};
