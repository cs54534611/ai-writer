// AI Writer 前端类型定义

export interface Character {
  id: string
  project_id?: string
  name: string
  aliases?: string[]
  gender?: string
  age?: string
  appearance?: string
  personality?: string
  background?: string
  arc?: string
  avatar_url?: string
  created_at: string
  updated_at: string
}

export interface CreateCharacterInput {
  name: string
  aliases?: string[]
  gender?: string
  age?: string
  personality?: string
  background?: string
  arc?: string
}

export interface Relationship {
  id: string
  project_id?: string
  from_character_id: string
  to_character_id: string
  relation_type: string
  direction: 'unidirectional' | 'bidirectional'
  strength: number
  created_at: string
}

export interface CreateRelationshipInput {
  project_id: string
  from_character_id: string
  to_character_id: string
  relation_type: string
  direction?: 'unidirectional' | 'bidirectional'
  strength?: number
}

export interface GraphData {
  nodes: { id: string; name: string; [key: string]: any }[]
  links: { source: string; target: string; type: string; strength: number }[]
}

export interface Inspiration {
  id: string
  project_id?: string
  content: string
  tags?: string[]
  related_setting_ids?: string[]
  created_at: string
}

export interface CreateInspirationInput {
  project_id: string
  content: string
  tags?: string[]
}

export type InspirationTag = 'character' | 'scene' | 'plot' | 'dialogue' | 'setting'

export interface Project {
  id: string
  name: string
  genre?: string
  description?: string
  total_words_target: number
  status: 'active' | 'archived' | 'draft' | 'deleted'
  created_at: string
  updated_at: string
}

export interface Chapter {
  id: string
  project_id?: string
  outline_id?: string
  title: string
  content: string
  word_count: number
  status: 'draft' | 'writing' | 'completed' | 'reviewed'
  sort_order: number
  created_at: string
  updated_at: string
}

export interface OutlineNode {
  id: string
  parent_id?: string
  title: string
  summary?: string
  word_target?: number
  narrative_pov?: string
  sort_order: number
  line_type: 'main' | 'branch' | 'subplot'
  children?: OutlineNode[]
}

export interface WorldSetting {
  id: string
  project_id?: string
  category: '人物' | '地点' | '物品' | '组织' | '概念'
  name: string
  content: string
  related_setting_ids?: string[]
}

export interface Location {
  id: string
  project_id?: string
  name: string
  parent_id?: string
  layer: string
  position_x: number
  position_y: number
  terrain?: string
  description?: string
}

export interface AIFeedback {
  score: number
  suggestions: string[]
}
