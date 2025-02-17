
import React, { useCallback, useState } from 'react';
import { useToast } from "@/hooks/use-toast";
import { Upload, File, AlertCircle, Loader2, CheckCircle2 } from 'lucide-react';
import { Progress } from "@/components/ui/progress";

type FileStatus = 'idle' | 'uploading' | 'success' | 'error';

interface FileInfo {
  file: File;
  progress: number;
  status: FileStatus;
}

const FileUpload = () => {
  const [files, setFiles] = useState<FileInfo[]>([]);
  const [isDragging, setIsDragging] = useState(false);
  const { toast } = useToast();

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setIsDragging(true);
    } else if (e.type === 'dragleave') {
      setIsDragging(false);
    }
  }, []);

  const updateFileProgress = (fileName: string, progress: number) => {
    setFiles(prev => 
      prev.map(fileInfo => 
        fileInfo.file.name === fileName 
          ? { ...fileInfo, progress }
          : fileInfo
      )
    );
  };

  const updateFileStatus = (fileName: string, status: FileStatus) => {
    setFiles(prev => 
      prev.map(fileInfo => 
        fileInfo.file.name === fileName 
          ? { ...fileInfo, status }
          : fileInfo
      )
    );
  };

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    const droppedFiles = Array.from(e.dataTransfer.files);
    handleFiles(droppedFiles);
  }, []);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const selectedFiles = Array.from(e.target.files);
      handleFiles(selectedFiles);
    }
  };

  const handleFiles = (newFiles: File[]) => {
    const fileInfos: FileInfo[] = newFiles.map(file => ({
      file,
      progress: 0,
      status: 'idle'
    }));

    setFiles(prev => [...prev, ...fileInfos]);

    fileInfos.forEach(fileInfo => {
      simulateFileUpload(fileInfo.file);
    });
  };

  const simulateFileUpload = (file: File) => {
    updateFileStatus(file.name, 'uploading');
    
    let progress = 0;
    const interval = setInterval(() => {
      progress += 5;
      updateFileProgress(file.name, progress);
      
      if (progress >= 100) {
        clearInterval(interval);
        updateFileStatus(file.name, 'success');
        toast({
          title: "Upload Complete",
          description: `${file.name} has been uploaded successfully.`,
        });
      }
    }, 100);
  };

  const getStatusIcon = (status: FileStatus) => {
    switch (status) {
      case 'uploading':
        return <Loader2 className="h-4 w-4 animate-spin" />;
      case 'success':
        return <CheckCircle2 className="h-4 w-4 text-green-500" />;
      case 'error':
        return <AlertCircle className="h-4 w-4 text-red-500" />;
      default:
        return <File className="h-4 w-4" />;
    }
  };

  return (
    <div className="w-full max-w-2xl mx-auto p-6 space-y-6">
      <div
        className={`relative rounded-lg border-2 border-dashed p-12 transition-all duration-300 ease-in-out ${
          isDragging 
            ? 'border-primary bg-primary/5 scale-[1.02]' 
            : 'border-gray-200 hover:border-primary/50 hover:bg-gray-50'
        }`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <input
          type="file"
          multiple
          className="hidden"
          onChange={handleFileSelect}
          id="fileInput"
        />
        
        <label
          htmlFor="fileInput"
          className="flex flex-col items-center justify-center gap-4 cursor-pointer"
        >
          <div className="p-4 rounded-full bg-primary/5">
            <Upload className="h-6 w-6 text-primary/80" />
          </div>
          <div className="text-center space-y-2">
            <h3 className="text-lg font-medium">
              Drag & drop files or <span className="text-primary hover:underline">browse</span>
            </h3>
            <p className="text-sm text-gray-500">
              Supports images, documents, and other file types
            </p>
          </div>
        </label>
      </div>

      {files.length > 0 && (
        <div className="space-y-4 animate-fadeIn">
          {files.map((fileInfo, index) => (
            <div
              key={fileInfo.file.name + index}
              className="glass rounded-lg p-4 transition-all duration-300"
            >
              <div className="flex items-center gap-4">
                {getStatusIcon(fileInfo.status)}
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium truncate">
                    {fileInfo.file.name}
                  </p>
                  <p className="text-xs text-gray-500">
                    {(fileInfo.file.size / 1024 / 1024).toFixed(2)} MB
                  </p>
                </div>
                <span className="text-xs text-gray-500">
                  {fileInfo.progress}%
                </span>
              </div>
              <Progress 
                value={fileInfo.progress} 
                className="h-1 mt-2"
              />
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default FileUpload;
