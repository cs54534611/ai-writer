import { useState } from 'react'

export interface Plugin {
  id: string
  name: string
  version: string
  description: string
  author: string
  hooks: string[]
  enabled: boolean
  config: Record<string, any>
  source: 'builtin' | 'thirdparty'
}

interface PluginCardProps {
  plugin: Plugin
  onToggle: (pluginId: string, enabled: boolean) => Promise<void>
  onSaveConfig: (pluginId: string, config: Record<string, any>) => Promise<void>
  onExecute: (pluginId: string) => Promise<void>
  loading?: boolean
}

export default function PluginCard({
  plugin,
  onToggle,
  onSaveConfig,
  onExecute,
  loading = false,
}: PluginCardProps) {
  const [expanded, setExpanded] = useState(false)
  const [config, setConfig] = useState<Record<string, any>>(plugin.config || {})
  const [saving, setSaving] = useState(false)
  const [executing, setExecuting] = useState(false)

  const handleToggle = async () => {
    await onToggle(plugin.id, !plugin.enabled)
  }

  const handleSaveConfig = async () => {
    setSaving(true)
    try {
      await onSaveConfig(plugin.id, config)
    } finally {
      setSaving(false)
    }
  }

  const handleExecute = async () => {
    setExecuting(true)
    try {
      await onExecute(plugin.id)
    } finally {
      setExecuting(false)
    }
  }

  const renderConfigField = (key: string, value: any) => {
    const inputId = `config-${plugin.id}-${key}`

    if (typeof value === 'boolean') {
      return (
        <label key={key} className="config-field">
          <span>{key}</span>
          <input
            id={inputId}
            type="checkbox"
            checked={config[key] ?? value}
            onChange={(e) => setConfig({ ...config, [key]: e.target.checked })}
          />
        </label>
      )
    }

    if (typeof value === 'number') {
      return (
        <label key={key} className="config-field">
          <span>{key}</span>
          <input
            id={inputId}
            type="number"
            value={config[key] ?? value}
            onChange={(e) => setConfig({ ...config, [key]: Number(e.target.value) })}
          />
        </label>
      )
    }

    if (typeof value === 'string') {
      return (
        <label key={key} className="config-field">
          <span>{key}</span>
          <input
            id={inputId}
            type="text"
            value={config[key] ?? value}
            onChange={(e) => setConfig({ ...config, [key]: e.target.value })}
          />
        </label>
      )
    }

    return null
  }

  return (
    <div className={`plugin-card ${expanded ? 'expanded' : ''}`}>
      <div className="plugin-card-header" onClick={() => setExpanded(!expanded)}>
        <div className="plugin-info">
          <h3>{plugin.name}</h3>
          <span className="plugin-version">v{plugin.version}</span>
          <span className={`plugin-source source-${plugin.source}`}>
            {plugin.source === 'builtin' ? '内置' : '第三方'}
          </span>
        </div>
        <label className="toggle-switch" onClick={(e) => e.stopPropagation()}>
          <input
            type="checkbox"
            checked={plugin.enabled}
            onChange={handleToggle}
            disabled={loading}
          />
          <span className="toggle-slider"></span>
        </label>
      </div>

      <p className="plugin-description">{plugin.description}</p>

      <div className="plugin-hooks">
        {plugin.hooks.map((hook) => (
          <span key={hook} className="hook-tag">
            {hook}
          </span>
        ))}
      </div>

      {expanded && (
        <div className="plugin-config-section">
          <h4>配置</h4>
          <div className="config-form">
            {Object.entries(plugin.config || {}).map(([key, value]) =>
              renderConfigField(key, value)
            )}
          </div>
          <div className="config-actions">
            <button
              className="btn-secondary"
              onClick={handleSaveConfig}
              disabled={saving || loading}
            >
              {saving ? '保存中...' : '保存配置'}
            </button>
            <button
              className="btn-primary"
              onClick={handleExecute}
              disabled={executing || loading || !plugin.enabled}
            >
              {executing ? '执行中...' : '执行'}
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
