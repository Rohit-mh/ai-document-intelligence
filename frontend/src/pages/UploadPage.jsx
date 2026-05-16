import React, { useState } from 'react'
import { FileUploader, Button, Alert } from '../components'
import { uploadDocument } from '../services'
import { useNotification } from '../hooks'

export const UploadPage = ({ onDocumentUploaded }) => {
  const [isUploading, setIsUploading] = useState(false)
  const [uploadError, setUploadError] = useState(null)
  const { notification, showNotification } = useNotification()

  const handleFileSelect = async (file, onProgress) => {
    setIsUploading(true)
    setUploadError(null)

    try {
      const result = await uploadDocument(file, (progress) => {
        onProgress(progress)
      })

      showNotification(
        `Document "${file.name}" uploaded successfully!`,
        'success'
      )

      if (onDocumentUploaded) {
        const docId = result.doc_id
        if (!docId) {
          throw new Error('Upload succeeded but server did not return doc_id.')
        }
        onDocumentUploaded({
          id: docId,
          doc_id: docId,
          name: result.file_name || file.name,
          uploadedAt: new Date().toISOString(),
          status: result.status || 'processed',
          size: file.size
        })
      }
    } catch (error) {
      console.error('Upload failed:', error)
      setUploadError(error.message)
      showNotification(error.message, 'error')
    } finally {
      setIsUploading(false)
    }
  }

  return (
    <div className="max-w-2xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-zinc-100 mb-2">Upload Document</h1>
        <p className="text-zinc-400">
          Upload a document to analyze and extract insights using AI
        </p>
      </div>

      {/* Upload Area */}
      <div className="bg-zinc-900/50 rounded-2xl border border-zinc-800 p-8 mb-6">
        <FileUploader
          onFileSelect={handleFileSelect}
          accept=".pdf,.docx,.txt"
          maxSize={50 * 1024 * 1024}
        />
      </div>

      {/* Features */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-zinc-900/50 border border-zinc-800 rounded-2xl p-6">
          <div className="text-3xl mb-2">📋</div>
          <h3 className="font-semibold text-zinc-100 mb-1">Auto Extract</h3>
          <p className="text-sm text-zinc-400">
            Automatically extract text from PDFs, Word documents, and text files
          </p>
        </div>

        <div className="bg-zinc-900/50 border border-zinc-800 rounded-2xl p-6">
          <div className="text-3xl mb-2">🧠</div>
          <h3 className="font-semibold text-zinc-100 mb-1">AI Analysis</h3>
          <p className="text-sm text-zinc-400">
            Generate summaries, extract insights, and answer questions using advanced AI
          </p>
        </div>

        <div className="bg-zinc-900/50 border border-zinc-800 rounded-2xl p-6">
          <div className="text-3xl mb-2">⚡</div>
          <h3 className="font-semibold text-zinc-100 mb-1">Fast Processing</h3>
          <p className="text-sm text-zinc-400">
            Process documents in seconds with our high-performance backend
          </p>
        </div>
      </div>

      {/* Errors */}
      {uploadError && (
        <div className="mt-6">
          <Alert variant="error">{uploadError}</Alert>
        </div>
      )}
    </div>
  )
}
