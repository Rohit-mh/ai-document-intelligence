import React, { useState } from 'react'
import { Card, Button, LoadingSpinner, Alert, Badge } from '../components'
import { getConciseSummary, getDetailedSummary, getInsights } from '../services'
import { useAsync } from '../hooks'

const SummaryTab = ({ document, onSummaryGenerated }) => {
  const [summaryType, setSummaryType] = useState('concise')
  const [summary, setSummary] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleGenerateSummary = async () => {
    setIsLoading(true)
    setError(null)

    try {
      const result = summaryType === 'concise'
        ? await getConciseSummary(document.id)
        : await getDetailedSummary(document.id)

      setSummary(result.summary)
      onSummaryGenerated?.(result)
    } catch (err) {
      setError(err.message)
    } finally {
      setIsLoading(false)
    }
  }

  if (!document) {
    return (
      <div className="text-center py-12 text-gray-500">
        Select a document to view its summary
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <div className="flex gap-2">
        <button
          onClick={() => setSummaryType('concise')}
          className={`px-4 py-2 rounded-lg font-medium transition-colors ${
            summaryType === 'concise'
              ? 'bg-primary-600 text-white'
              : 'bg-gray-200 text-gray-900 hover:bg-gray-300'
          }`}
        >
          Concise
        </button>
        <button
          onClick={() => setSummaryType('detailed')}
          className={`px-4 py-2 rounded-lg font-medium transition-colors ${
            summaryType === 'detailed'
              ? 'bg-primary-600 text-white'
              : 'bg-gray-200 text-gray-900 hover:bg-gray-300'
          }`}
        >
          Detailed
        </button>
        <Button
          onClick={handleGenerateSummary}
          loading={isLoading}
          className="ml-auto"
        >
          Generate
        </Button>
      </div>

      {error && <Alert variant="error">{error}</Alert>}

      {isLoading ? (
        <div className="flex items-center justify-center py-12">
          <LoadingSpinner />
        </div>
      ) : summary ? (
        <Card className="bg-blue-50">
          <p className="text-gray-700 whitespace-pre-wrap">{summary}</p>
        </Card>
      ) : (
        <Card className="text-center py-12 text-gray-500">
          Generate a summary to see results
        </Card>
      )}
    </div>
  )
}

const InsightsTab = ({ document }) => {
  const [insights, setInsights] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleExtractInsights = async () => {
    setIsLoading(true)
    setError(null)

    try {
      const result = await getInsights(document.id)
      if (result.raw_insights) {
        setInsights({ analysis: result.raw_insights })
      } else {
        const { status: _s, doc_id: _d, raw_insights: _r, ...rest } = result
        setInsights(rest)
      }
    } catch (err) {
      setError(err.message)
    } finally {
      setIsLoading(false)
    }
  }

  if (!document) {
    return (
      <div className="text-center py-12 text-gray-500">
        Select a document to extract insights
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <Button
        onClick={handleExtractInsights}
        loading={isLoading}
      >
        Extract Insights
      </Button>

      {error && <Alert variant="error">{error}</Alert>}

      {isLoading ? (
        <div className="flex items-center justify-center py-12">
          <LoadingSpinner />
        </div>
      ) : insights ? (
        <div className="space-y-4">
          {Object.entries(insights).map(([key, value]) => (
            <Card key={key}>
              <h3 className="font-semibold text-gray-900 mb-2 capitalize">
                {key.replace(/_/g, ' ')}
              </h3>
              {Array.isArray(value) ? (
                <ul className="space-y-2">
                  {value.map((item, idx) => (
                    <li key={idx} className="flex gap-2 text-sm text-zinc-300">
                      <span className="text-primary-600">•</span>
                      <span>{item}</span>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-sm text-zinc-300">{value}</p>
              )}
            </Card>
          ))}
        </div>
      ) : (
        <Card className="text-center py-12 text-gray-500">
          Extract insights to see results
        </Card>
      )}
    </div>
  )
}

export const DashboardPage = ({ documents = [], selectedDocumentId = null }) => {
  const [activeTab, setActiveTab] = useState('summary')
  const [selectedDocument, setSelectedDocument] = useState(
    documents.find(d => d.id === selectedDocumentId) || documents[0] || null
  )

  if (documents.length === 0) {
    return (
      <div className="text-center py-12">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">Dashboard</h1>
        <p className="text-gray-600 mb-6">No documents uploaded yet</p>
        <Button onClick={() => window.location.href = '/'}>
          Upload Your First Document
        </Button>
      </div>
    )
  }

  return (
    <div>
      <h1 className="text-3xl font-bold text-zinc-100 mb-8">Dashboard</h1>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Document List */}
        <div className="lg:col-span-1">
          <h2 className="font-semibold text-zinc-100 mb-4">Documents</h2>
          <div className="space-y-2">
            {documents.map(doc => (
              <button
                key={doc.id}
                onClick={() => setSelectedDocument(doc)}
                className={`w-full text-left px-4 py-2 rounded-lg transition-colors ${
                  selectedDocument?.id === doc.id
                    ? 'bg-zinc-100 text-zinc-950 shadow-lg'
                    : 'bg-zinc-800 text-zinc-300 hover:bg-zinc-700'
                }`}
              >
                <p className="text-sm font-medium truncate">{doc.name}</p>
              </button>
            ))}
          </div>
        </div>

        {/* Content Area */}
        <div className="lg:col-span-3">
          {/* Tabs */}
          <div className="flex gap-2 mb-6 border-b">
            {['summary', 'insights'].map(tab => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`px-4 py-2 font-medium border-b-2 transition-colors ${
                  activeTab === tab
                    ? 'border-zinc-100 text-zinc-100'
                    : 'border-transparent text-zinc-500 hover:text-zinc-300'
                }`}
              >
                {tab.charAt(0).toUpperCase() + tab.slice(1)}
              </button>
            ))}
          </div>

          {/* Tab Content */}
          {activeTab === 'summary' && (
            <SummaryTab document={selectedDocument} />
          )}
          {activeTab === 'insights' && (
            <InsightsTab document={selectedDocument} />
          )}
        </div>
      </div>
    </div>
  )
}
