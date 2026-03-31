import { useState, useEffect } from 'react'
import { usePlugins, Plugin } from '../hooks/usePlugins'
import PluginCard from '../components/PluginCard'

type FilterType = 'all' | 'enabled' | 'disabled'
type TabType = 'installed' | 'market'

interface MarketPlugin {
  id: string
  name: string
  description: string
  author: string
  downloads: number
  rating: number
  tags: string[]
}

export default function PluginsPage() {
  const {
    loading,
    error,
    getPlugins,
    enablePlugin,
    disablePlugin,
    savePluginConfig,
    executePlugin,
  } = usePlugins()

  const [plugins, setPlugins] = useState<Plugin[]>([])
  const [filter, setFilter] = useState<FilterType>('all')
  const [scanning, setScanning] = useState(false)
  const [activeTab, setActiveTab] = useState<TabType>('installed')
  const [marketPlugins, setMarketPlugins] = useState<MarketPlugin[]>([])
  const [marketLoading, setMarketLoading] = useState(false)
  const [installing, setInstalling] = useState<string | null>(null)

  useEffect(() => {
    loadPlugins()
    if (activeTab === 'market') {
      loadMarketPlugins()
    }
  }, [activeTab])

  const loadPlugins = async () => {
    try {
      const data = await getPlugins()
      setPlugins(data)
    } catch (err) {
      console.error('Failed to load plugins:', err)
    }
  }

  const loadMarketPlugins = async () => {
    setMarketLoading(true)
    try {
      const response = await fetch('/api/v1/plugins/market')
      if (response.ok) {
        const data = await response.json()
        setMarketPlugins(data)
      }
    } catch (err) {
      console.error('Failed to load market plugins:', err)
    } finally {
      setMarketLoading(false)
    }
  }

  const handleToggle = async (pluginId: string, enabled: boolean) => {
    try {
      if (enabled) {
        await enablePlugin(pluginId)
      } else {
        await disablePlugin(pluginId)
      }
      setPlugins(plugins.map(p =>
        p.id === pluginId ? { ...p, enabled } : p
      ))
    } catch (err) {
      console.error('Failed to toggle plugin:', err)
    }
  }

  const handleSaveConfig = async (pluginId: string, config: Record<string, any>) => {
    await savePluginConfig(pluginId, config)
    setPlugins(plugins.map(p =>
      p.id === pluginId ? { ...p, config } : p
    ))
  }

  const handleExecute = async (pluginId: string) => {
    await executePlugin(pluginId, { projectId: 'current' })
  }

  const handleInstall = async (pluginId: string) => {
    setInstalling(pluginId)
    try {
      const response = await fetch(`/api/v1/plugins/${pluginId}/install`, {
        method: 'POST',
      })
      if (response.ok) {
        const result = await response.json()
        if (result.success) {
          alert(result.message)
          // 刷新已安装插件列表
          loadPlugins()
        }
      }
    } catch (err) {
      console.error('Failed to install plugin:', err)
    } finally {
      setInstalling(null)
    }
  }

  const handleScan = async () => {
    setScanning(true)
    try {
      // Re-fetch plugins after scan
      await loadPlugins()
    } finally {
      setScanning(false)
    }
  }

  const filteredPlugins = plugins.filter(p => {
    if (filter === 'enabled') return p.enabled
    if (filter === 'disabled') return !p.enabled
    return true
  })

  const renderStars = (rating: number) => {
    const stars = []
    const fullStars = Math.floor(rating)
    for (let i = 0; i < 5; i++) {
      if (i < fullStars) {
        stars.push(<span key={i} className="star filled">★</span>)
      } else {
        stars.push(<span key={i} className="star">☆</span>)
      }
    }
    return <div className="rating">{stars} <span className="rating-value">{rating.toFixed(1)}</span></div>
  }

  return (
    <div className="plugins-page">
      <header className="page-header">
        <h1>插件管理</h1>
        <button
          className="btn-primary"
          onClick={handleScan}
          disabled={scanning || loading}
        >
          {scanning ? '扫描中...' : '扫描插件'}
        </button>
      </header>

      {error && <div className="error-message">{error}</div>}

      <div className="tabs">
        <button
          className={`tab ${activeTab === 'installed' ? 'active' : ''}`}
          onClick={() => setActiveTab('installed')}
        >
          已安装
        </button>
        <button
          className={`tab ${activeTab === 'market' ? 'active' : ''}`}
          onClick={() => setActiveTab('market')}
        >
          插件市场
        </button>
      </div>

      {activeTab === 'installed' && (
        <>
          <div className="filter-tabs">
            <button
              className={`tab ${filter === 'all' ? 'active' : ''}`}
              onClick={() => setFilter('all')}
            >
              全部 ({plugins.length})
            </button>
            <button
              className={`tab ${filter === 'enabled' ? 'active' : ''}`}
              onClick={() => setFilter('enabled')}
            >
              已启用 ({plugins.filter(p => p.enabled).length})
            </button>
            <button
              className={`tab ${filter === 'disabled' ? 'active' : ''}`}
              onClick={() => setFilter('disabled')}
            >
              已禁用 ({plugins.filter(p => !p.enabled).length})
            </button>
          </div>

          {loading && plugins.length === 0 ? (
            <div className="loading">加载中...</div>
          ) : filteredPlugins.length === 0 ? (
            <div className="empty-state">
              <p>暂无插件</p>
              <p className="hint">点击「扫描插件」发现新插件</p>
            </div>
          ) : (
            <div className="plugins-grid">
              {filteredPlugins.map(plugin => (
                <PluginCard
                  key={plugin.id}
                  plugin={plugin}
                  onToggle={handleToggle}
                  onSaveConfig={handleSaveConfig}
                  onExecute={handleExecute}
                  loading={loading}
                />
              ))}
            </div>
          )}
        </>
      )}

      {activeTab === 'market' && (
        <div className="market-section">
          {marketLoading ? (
            <div className="loading">加载市场中...</div>
          ) : (
            <div className="market-grid">
              {marketPlugins.map(plugin => (
                <div key={plugin.id} className="market-card">
                  <div className="market-card-header">
                    <h3>{plugin.name}</h3>
                    {renderStars(plugin.rating)}
                  </div>
                  <p className="market-description">{plugin.description}</p>
                  <div className="market-meta">
                    <span className="author">作者: {plugin.author}</span>
                    <span className="downloads">下载: {plugin.downloads}</span>
                  </div>
                  <div className="market-tags">
                    {plugin.tags.map(tag => (
                      <span key={tag} className="tag">{tag}</span>
                    ))}
                  </div>
                  <button
                    className="btn-install"
                    onClick={() => handleInstall(plugin.id)}
                    disabled={installing === plugin.id || plugins.some(p => p.id === plugin.id)}
                  >
                    {installing === plugin.id ? '安装中...' : 
                     plugins.some(p => p.id === plugin.id) ? '已安装' : '安装'}
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      <footer className="page-footer">
        {activeTab === 'installed' && (
          <div className="market-hint">
            <span>🎉 发现更多插件</span>
            <button className="btn-link" onClick={() => setActiveTab('market')}>
              前往插件市场
            </button>
          </div>
        )}
      </footer>
    </div>
  )
}
