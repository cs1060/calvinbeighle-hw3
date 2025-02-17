import { useState } from 'react'
import { uploadFiles } from '../lib/api'
import { useDropzone } from 'react-dropzone'

export function DropZone() {
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<any | null>(null)

  const onDrop = async (acceptedFiles: File[]) => {
    setUploading(true)
    setError(null)
    try {
      const result = await uploadFiles(acceptedFiles)
      setSuccess(result)
      console.log('Upload successful:', result)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed')
      console.error('Upload error:', err)
    } finally {
      setUploading(false)
    }
  }

  const { getRootProps, getInputProps, isDragActive } = useDropzone({ onDrop })

  return (
    <div className="flex flex-col items-center">
      <h1 className="text-4xl font-bold mb-8">Gnome</h1>
      <div
        {...getRootProps()}
        className={`w-full max-w-xl p-6 border-2 border-dashed rounded-lg 
          ${isDragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300'}`}
      >
        <input {...getInputProps()} />
        {uploading ? (
          <p className="text-center">Uploading...</p>
        ) : (
          <p className="text-center">Drag & drop files here, or click to select files</p>
        )}
      </div>

      {error && <div className="mt-4 text-red-500">{error}</div>}
      
      {success && (
        <div className="mt-4 text-green-500">
          <p>{success.message}</p>
          <pre className="mt-2 text-sm">
            {JSON.stringify(success.stats, null, 2)}
          </pre>
        </div>
      )}
    </div>
  )
} 