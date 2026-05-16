import React from 'react'
import { Card, Badge } from './Common'

export const DocumentCard = ({ 
  document, 
  onSelect, 
  isSelected = false,
  onClick
}) => {
  const getFileIcon = (filename) => {
    if (filename.endsWith('.pdf')) return '📄'
    if (filename.endsWith('.docx')) return '📝'
    if (filename.endsWith('.txt')) return '📋'
    return '📑'
  }

  const formatDate = (dateString) => {
    try {
      return new Date(dateString).toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    } catch {
      return 'Unknown'
    }
  }

  return (
    <Card
      onClick={onClick}
      className={`cursor-pointer transition-all duration-200 ${
        isSelected 
          ? 'border-2 border-primary-600 shadow-lg' 
          : 'hover:shadow-lg'
      }`}
    >
      <div className="flex items-start justify-between">
        <div className="flex items-start gap-4 flex-1">
          <div className="text-3xl">{getFileIcon(document.name)}</div>
          <div className="flex-1 min-w-0">
            <h3 className="font-semibold text-gray-900 truncate">
              {document.name}
            </h3>
            <p className="text-sm text-gray-500 mt-1">
              {formatDate(document.uploadedAt)}
            </p>
            <div className="flex gap-2 mt-2 flex-wrap">
              {document.status === 'processed' && (
                <Badge variant="green">Processed</Badge>
              )}
              {document.status === 'processing' && (
                <Badge variant="yellow">Processing</Badge>
              )}
              {document.hasInsights && (
                <Badge variant="blue">Insights</Badge>
              )}
            </div>
          </div>
        </div>
      </div>
      {document.summary && (
        <div className="mt-4 p-3 bg-gray-50 rounded">
          <p className="text-sm text-gray-600 line-clamp-2">
            {document.summary}
          </p>
        </div>
      )}
    </Card>
  )
}

export const DocumentGrid = ({ documents, onSelect, selectedId }) => {
  if (!documents || documents.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">No documents uploaded yet</p>
      </div>
    )
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {documents.map((doc) => (
        <DocumentCard
          key={doc.id}
          document={doc}
          onSelect={() => onSelect(doc)}
          isSelected={selectedId === doc.id}
          onClick={() => onSelect(doc)}
        />
      ))}
    </div>
  )
}
