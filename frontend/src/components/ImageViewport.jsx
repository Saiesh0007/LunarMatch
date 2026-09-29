import React, { useRef, useState, useEffect } from 'react';
import { Icon } from './ui/Icon.jsx';
import { Button } from './ui/Button.jsx';
import { apiClient } from '../api/client.js';
import { motion, AnimatePresence } from 'framer-motion';

export function ImageViewport({ file, roleId, label, onUpload }) {
  const fileInputRef = useRef(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
  const [uploadError, setUploadError] = useState(null);

  useEffect(() => {
    if (!file) {
      setImagePreview(null);
      setUploadError(null);
    } else if (file.rawFile) {
      const url = URL.createObjectURL(file.rawFile);
      setImagePreview(url);
      return () => URL.revokeObjectURL(url);
    } else if (file.imageId) {
      setImagePreview(apiClient.getPreviewUrl(file.imageId));
    }
  }, [file]);

  const handleUploadClick = () => {
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
      fileInputRef.current.click();
    }
  };

  const processFile = async (selectedFile) => {
    if (!selectedFile) return;
    setUploadError(null);
    setIsUploading(true);

    try {
      const data = await apiClient.uploadImage(selectedFile);
      const sizeInMB = (selectedFile.size / (1024 * 1024)).toFixed(2);

      if (onUpload) {
        onUpload({
          name: selectedFile.name,
          size: `${sizeInMB} MB`,
          rawFile: selectedFile,
          imageId: data.image_id
        });
      }
    } catch (err) {
      console.error("Upload failed:", err);
      setUploadError(err.message || "Failed to upload image to server");
    } finally {
      setIsUploading(false);
    }
  };

  const handleFileChange = (e) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      processFile(selectedFile);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
    const droppedFile = e.dataTransfer.files?.[0];
    if (droppedFile) {
      processFile(droppedFile);
    }
  };

  return (
    <div
      className={`h-[400px] w-full rounded-xl border relative overflow-hidden flex flex-col transition-all group shadow-xl ${
        isDragging
          ? 'border-primary ring-2 ring-primary/40 bg-surface-container'
          : file
            ? 'border-surface-container-high bg-[#050505]'
            : 'border-dashed border-outline-variant bg-surface-container-lowest hover:border-primary/50'
      }`}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
    >
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileChange}
        className="hidden"
        accept="image/*,.tif,.tiff,.png,.jpg,.jpeg"
      />

      {/* Decorative Grid (Background) */}
      {!imagePreview && (
        <div
          className="absolute inset-0 bg-surface-container-lowest opacity-25 pointer-events-none"
          style={{ backgroundImage: 'linear-gradient(#2a2a2a 1px, transparent 1px), linear-gradient(90deg, #2a2a2a 1px, transparent 1px)', backgroundSize: '32px 32px' }}
        />
      )}

      {/* Target Crosshair */}
      {imagePreview && (
        <div className="absolute inset-0 flex items-center justify-center z-10 text-primary opacity-20 pointer-events-none mix-blend-difference">
          <div className="w-[1px] h-full bg-primary/30 absolute" />
          <div className="h-[1px] w-full bg-primary/30 absolute" />
          <Icon name="add" size="64px" />
        </div>
      )}

      {/* Main Content Area */}
      <div className="flex-1 w-full h-full relative z-0 flex items-center justify-center">
        {imagePreview ? (
          <img
            src={imagePreview}
            className="w-full h-full object-cover transition-transform duration-700 ease-out group-hover:scale-[1.02]"
            alt={label || 'Lunar frame'}
            onError={(e) => {
              console.warn("Failed to load image preview:", imagePreview);
              setUploadError("Image preview could not be rendered");
            }}
          />
        ) : (
          <div
            onClick={handleUploadClick}
            className="flex flex-col items-center justify-center gap-3 z-10 p-6 rounded-2xl bg-surface-container/60 backdrop-blur-sm border border-surface-container-high cursor-pointer hover:bg-surface-container hover:border-outline-variant transition-all max-w-sm text-center"
          >
            <div className="w-14 h-14 rounded-full bg-surface-container-high flex items-center justify-center text-primary shadow-inner">
              <Icon name={isDragging ? "download" : "cloud_upload"} size="32px" />
            </div>
            <div>
              <div className="font-headline-sm text-primary uppercase tracking-wider text-sm font-semibold">
                {isDragging ? 'Drop Image Here' : 'Select or Drop Image'}
              </div>
              <p className="font-body-md text-xs text-outline-variant mt-1">
                Supports PNG, JPG, TIFF lunar satellite & optical telemetry imagery.
              </p>
            </div>
            <Button
              type="button"
              variant="primary"
              icon="upload"
              size="sm"
              className="mt-1 font-mono text-xs"
              onClick={(e) => {
                e.stopPropagation();
                handleUploadClick();
              }}
            >
              Browse Files
            </Button>
          </div>
        )}
      </div>

      {/* Uploading Overlay */}
      <AnimatePresence>
        {isUploading && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="absolute inset-0 bg-black/80 backdrop-blur-md z-30 flex flex-col items-center justify-center gap-3"
          >
            <div className="animate-spin text-primary p-3 rounded-full border border-surface-container-highest">
              <Icon name="progress_activity" size="28px" />
            </div>
            <div className="font-mono text-xs text-primary uppercase tracking-widest font-semibold">
              Ingesting Image into Pipeline...
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Error Banner Overlay */}
      {uploadError && (
        <div className="absolute top-14 left-4 right-4 z-30 bg-error/90 text-on-error p-3 rounded-lg text-xs font-mono flex items-center justify-between shadow-lg">
          <div className="flex items-center gap-2">
            <Icon name="error" size="18px" />
            <span>{uploadError}</span>
          </div>
          <button
            type="button"
            onClick={() => setUploadError(null)}
            className="text-on-error hover:opacity-80 font-bold"
          >
            ✕
          </button>
        </div>
      )}

      {/* Top Bar overlays */}
      <div className="absolute top-4 left-4 flex gap-2 z-20 pointer-events-none">
        <div className="bg-black/80 backdrop-blur-md border border-surface-container-high px-3 py-1.5 rounded font-mono text-[10px] text-primary uppercase shadow-md tracking-widest">
          {label}
        </div>
        {file && (
          <div className="bg-black/80 backdrop-blur-md border border-surface-container-high px-3 py-1.5 rounded font-mono text-[10px] text-outline shadow-md">
            {file.size || 'AUTO'}
          </div>
        )}
      </div>

      {/* Bottom info bar when file is present */}
      <AnimatePresence>
        {file && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 10 }}
            className="absolute bottom-3 left-3 right-3 z-20 flex flex-wrap justify-between items-center gap-2 bg-black/90 backdrop-blur-md border border-surface-container-high p-2.5 rounded-lg shadow-2xl"
          >
            {/* File Info */}
            <div className="flex items-center gap-2 min-w-0 flex-1">
              <Icon name="image" size="18px" className="text-primary flex-shrink-0" />
              <span className="font-mono text-xs text-primary truncate font-semibold" title={file.name}>
                {file.name}
              </span>
            </div>

            {/* Action Buttons */}
            <div className="flex items-center gap-2 flex-shrink-0">
              <Button
                type="button"
                variant="ghost"
                size="sm"
                icon="delete"
                className="font-mono text-xs text-outline-variant hover:text-error hover:border-error py-1.5 px-3"
                onClick={(e) => {
                  e.stopPropagation();
                  setImagePreview(null);
                  if (onUpload) onUpload(null);
                }}
              >
                Clear
              </Button>
              <Button
                type="button"
                variant="primary"
                size="sm"
                icon="upload"
                className="font-mono text-xs py-1.5 px-3"
                onClick={(e) => {
                  e.stopPropagation();
                  handleUploadClick();
                }}
              >
                Change
              </Button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
