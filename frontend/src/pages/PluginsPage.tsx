import { useState, useEffect } from 'react'
import { usePlugins, Plugin } from '../hooks/usePlugins'
import PluginCard from '../components/PluginCard'

type FilterType = 'all' | 'enabled' | 'disabled'

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

  useEffect(() => {
    loadPlugins()
  }, [])

  const loadPlugins = async () => {
    try {
      const data = await getPlugins()
      setPlugins(data)
    } catch (err) {
      console.error('Failed to load plugins:', err)
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

      <footer className="page-footer">
        <div className="marketplace-hint">
          <span className="coming-soon">🎉 插件市场敬请期待</span>
          <p>即将上线更多精彩插件</p>
        </div>
      </footer>
    </div>
  )
}
