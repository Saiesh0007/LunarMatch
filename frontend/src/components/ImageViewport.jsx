import React, { useRef, useState, useEffect } from 'react';
import { Icon } from './ui/Icon.jsx';
import { Button } from './ui/Button.jsx';
import { apiClient } from '../api/client.js';

export function ImageViewport({ file, roleId, label, onUpload }) {
  const fileInputRef = useRef(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [isUploading, setIsUploading] = useState(false);

  useEffect(() => {
    if (!file) {
      setImagePreview(null);
    } else if (file.imageId) {
      // If we loaded a sample or have an id, we can fetch the preview
      // URL.createObjectURL might not exist if it's from server
      if (!imagePreview) {
        setImagePreview(apiClient.getPreviewUrl(file.imageId));
      }
    }
  }, [file, imagePreview]);

  const handleUploadClick = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  const handleFileChange = async (e) => {
    const selectedFile = e.target.files[0];
    if (!selectedFile) return;

    const objectUrl = URL.createObjectURL(selectedFile);
    setImagePreview(objectUrl);

    try {
      setIsUploading(true);
      const data = await apiClient.uploadImage(selectedFile);

      if (onUpload) {
        const sizeInMB = (selectedFile.size / (1024 * 1024)).toFixed(2);
        onUpload({
          name: selectedFile.name,
          size: `${sizeInMB} MB`,
          rawFile: selectedFile,
          imageId: data.image_id
        });
      }
    } catch (err) {
      console.error("Upload failed:", err);
      alert("Failed to upload image to the server.");
    } finally {
      setIsUploading(false);
    }
  };

  if (!file) {
    return (
      <div className="h-[400px] bg-surface-container-lowest border border-dashed border-outline-variant hover:border-primary/50 transition-colors rounded-xl flex flex-col items-center justify-center text-outline-variant relative group overflow-hidden">
        <div className="absolute top-4 left-4 font-mono text-[10px] uppercase tracking-wider group-hover:text-primary transition-colors">{label}</div>
        
        <div className="flex flex-col items-center justify-center gap-4 z-10 p-6 rounded-2xl bg-surface-container/50 backdrop-blur-sm border border-surface-container-high pointer-events-none group-hover:bg-surface-container-low transition-colors">
          <Icon name="cloud_upload" size="48px" className="text-outline-variant group-hover:text-primary transition-colors" />
          <div className="text-center w-full max-w-sm">
            <div className="font-headline-sm text-primary uppercase tracking-wider mb-2">Configure Feed Data</div>
            <div className="font-body-md opacity-80 mb-6 text-sm">Upload lunar imagery dataset from local telemetry datastore for registration matching.</div>
          </div>
          
          <div className="pointer-events-auto">
             <Button variant="primary" icon="upload" onClick={handleUploadClick} className="shadow-lg shadow-primary/10">
               Upload File
             </Button>
          </div>
        </div>

        <input 
          type="file" 
          ref={fileInputRef} 
          onChange={handleFileChange} 
          className="hidden" 
          accept="image/*,.tif,.tiff"
        />

        {/* Decorative Grid */}
        <div className="absolute inset-0 bg-surface-container-lowest opacity-20 transition-opacity group-hover:opacity-40"
             style={{ backgroundImage: 'linear-gradient(#2a2a2a 1px, transparent 1px), linear-gradient(90deg, #2a2a2a 1px, transparent 1px)', backgroundSize: '40px 40px' }}>
        </div>
      </div>
    );
  }

  return (
    <div className="h-[400px] bg-[#050505] border border-surface-container-high rounded-xl relative overflow-hidden flex items-center justify-center group shadow-xl">
      {/* Either show uploaded image or decorative fallback/grid */}
      {imagePreview ? (
        <img src={imagePreview} className="w-full h-full object-cover opacity-90 transition-transform duration-[2s] ease-out group-hover:scale-[1.03] group-hover:opacity-100" alt={file.name} />
      ) : (
        <div className="absolute inset-0 bg-[#0a0a0a]"
             style={{ backgroundImage: 'linear-gradient(#222 1px, transparent 1px), linear-gradient(90deg, #222 1px, transparent 1px)', backgroundSize: '20px 20px' }}>
        </div>
      )}

      {isUploading && (
        <div className="absolute inset-0 bg-black/60 backdrop-blur-sm z-30 flex flex-col items-center justify-center">
          <div className="animate-spin text-primary mb-4 p-2 rounded-full border border-surface-container-highest">
            <Icon name="progress_activity" size="24px" />
          </div>
          <div className="font-mono text-xs text-primary uppercase tracking-widest">Uploading to Pipeline...</div>
        </div>
      )}

      {/* Target Crosshair */}
      <div className="absolute flex items-center justify-center z-10 text-primary opacity-30 pointer-events-none mix-blend-difference">
        <div className="w-[1px] h-[400px] bg-primary/40 absolute" />
        <div className="h-[1px] w-[400px] bg-primary/40 absolute" />
        <Icon name="add" size="80px" />
      </div>

      <div className="absolute top-4 left-4 flex gap-2 z-20 pointer-events-none">
        <div className="bg-black/70 backdrop-blur-md border border-surface-container px-3 py-1.5 rounded font-mono text-[10px] text-primary uppercase shadow-[0_4px_16px_rgba(0,0,0,0.5)] tracking-widest">{label}</div>
        <div className="bg-black/70 backdrop-blur-md border border-surface-container px-3 py-1.5 rounded font-mono text-[10px] text-outline-variant shadow-[0_4px_16px_rgba(0,0,0,0.5)]">{file.size}</div>
      </div>

      <div className="absolute top-4 right-4 z-20">
         <Button 
            variant="ghost" 
            className="!h-8 !px-3 font-mono text-[10px] text-error hover:bg-error-container/20 hover:text-error bg-black/70 backdrop-blur-md border border-surface-container shadow-[0_4px_16px_rgba(0,0,0,0.5)]"
            onClick={() => {
              setImagePreview(null);
              if (onUpload) onUpload(null);
            }}
          >
           DISCARD
         </Button>
      </div>
      
      <div className="absolute bottom-4 left-4 bg-black/80 backdrop-blur-md border border-surface-container-high p-3 rounded-lg z-20 font-mono text-[11px] text-outline-variant tracking-wide shadow-[0_4px_24px_rgba(0,0,0,1)] min-w-[200px]">
        <div className="flex justify-between items-center mb-2 border-b border-surface-container pb-2">
          <span>FILE:</span><span className="text-primary truncate ml-3 font-semibold max-w-[120px]" title={file.name}>{file.name}</span>
        </div>
        <div className="flex justify-between items-center mb-1 text-[10px]">
          <span>RES:</span><span className="text-on-surface">AUTO_FITTED</span>
        </div>
        <div className="flex justify-between items-center text-[10px]">
          <span>TYPE:</span><span className="text-on-surface">OPTICAL_RGB</span>
        </div>
      </div>
      
      <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-black/20 pointer-events-none" />
    </div>
  );
}
