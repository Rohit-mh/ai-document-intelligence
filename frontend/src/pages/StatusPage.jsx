import React, { useState, useEffect } from 'react'
import { Card, Badge, LoadingSpinner, Alert } from '../components'
import { getHealth, getStats } from '../services'

export const StatusPage = () => {
  const [health, setHealth] = useState(null)
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true)
        setError(null)

        const [healthData, statsData] = await Promise.all([
          getHealth(),
          getStats()
        ])

        setHealth(healthData)
        setStats(statsData)
      } catch (err) {
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
    const interval = setInterval(fetchData, 10000)

    return () => clearInterval(interval)
  }, [])

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <LoadingSpinner />
      </div>
    )
  }

  const cfg = stats?.config || {}
  const isHealthy = health?.healthy === true || health?.status === 'healthy'
  const chunkCount =
    health?.database?.chunk_count ??
    stats?.chroma_stats?.count ??
    stats?.total_chunks ??
    0

  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold text-zinc-100 mb-8">System Status</h1>

      {error && (
        <Alert variant="error" className="mb-6">
          {error}
        </Alert>
      )}

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <Card>
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-semibold text-zinc-100">Backend Health</h2>
            {isHealthy ? (
              <Badge variant="green">Healthy</Badge>
            ) : (
              <Badge variant="red">Unhealthy</Badge>
            )}
          </div>
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-zinc-400">Status:</span>
              <span className="font-medium">
                {health?.status || 'Unknown'}
              </span>
            </div>
            {health?.version && (
              <div className="flex justify-between text-sm">
                <span className="text-zinc-400">API version:</span>
                <span className="font-medium">{health.version}</span>
              </div>
            )}
          </div>
        </Card>

        <Card>
          <h2 className="font-semibold text-zinc-100 mb-4">Vector Database</h2>
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-zinc-400">Service:</span>
              <Badge variant="blue">ChromaDB</Badge>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-zinc-400">Chunks (approx.):</span>
              <span className="font-medium">{chunkCount}</span>
            </div>
          </div>
        </Card>

        <Card>
          <h2 className="font-semibold text-zinc-100 mb-4">AI Provider</h2>
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-zinc-400">Provider:</span>
              <Badge variant="purple">{(cfg.llm_provider || 'github').toString()}</Badge>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-zinc-400">Model:</span>
              <span className="font-medium text-xs break-all">
                {cfg.github_model || cfg.groq_model || '—'}
              </span>
            </div>
          </div>
        </Card>
      </div>

      {stats && (
        <Card className="mb-8">
          <h2 className="font-semibold text-zinc-100 mb-6">Statistics</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-zinc-100">
                {stats.total_documents ?? 0}
              </div>
              <p className="text-sm text-zinc-400 mt-1">Documents</p>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-zinc-100">
                {stats.total_chunks ?? stats.chroma_stats?.count ?? 0}
              </div>
              <p className="text-sm text-zinc-400 mt-1">Text Chunks</p>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-zinc-100">
                {(stats.total_embeddings ?? stats.total_chunks ?? 0).toLocaleString()}
              </div>
              <p className="text-sm text-zinc-400 mt-1">Embeddings</p>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-zinc-100">
                {(stats.database_size_mb ?? 0).toFixed(2)}
              </div>
              <p className="text-sm text-zinc-400 mt-1">Vector store (MB)</p>
            </div>
          </div>
        </Card>
      )}

      <Card>
        <h2 className="font-semibold text-zinc-100 mb-4">Configuration</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
          <div>
            <p className="text-zinc-400">API server (frontend env):</p>
            <p className="font-medium break-all">{import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_URL || 'http://localhost:8000'}</p>
          </div>
          <div>
            <p className="text-zinc-400">Embedding model:</p>
            <p className="font-medium break-all">{cfg.embedding_model || '—'}</p>
          </div>
          <div>
            <p className="text-zinc-400">Chroma collection:</p>
            <p className="font-medium">{cfg.collection_name || '—'}</p>
          </div>
          <div>
            <p className="text-zinc-400">Chunk size / overlap:</p>
            <p className="font-medium">
              {(cfg.chunk_size ?? '—')} / {(cfg.chunk_overlap ?? '—')}
            </p>
          </div>
        </div>
      </Card>
    </div>
  )
}
