/**
 * 语音输入 Hook - 使用浏览器 Web Speech API
 * 支持中文识别，可开始/停止监听，结果回调
 */

import { useState, useCallback, useRef, useEffect } from 'react'

export interface VoiceInputOptions {
  onResult?: (text: string) => void
  onError?: (error: string) => void
  continuous?: boolean
  interimResults?: boolean
}

export interface UseVoiceInputReturn {
  isListening: boolean
  transcript: string
  interimTranscript: string
  startListening: () => void
  stopListening: () => void
  resetTranscript: () => void
  isSupported: boolean
}

export function useVoiceInput(options: VoiceInputOptions = {}): UseVoiceInputReturn {
  const { onResult, onError, continuous = false, interimResults = true } = options
  
  const [isListening, setIsListening] = useState(false)
  const [transcript, setTranscript] = useState('')
  const [interimTranscript, setInterimTranscript] = useState('')
  
  const recognitionRef = useRef<SpeechRecognition | null>(null)
  const isSupported = useRef(false)
  
  // 检测浏览器支持
  useEffect(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
    isSupported.current = !!SpeechRecognition
    
    if (SpeechRecognition) {
      const recognition = new SpeechRecognition()
      recognition.continuous = continuous
      recognition.interimResults = interimResults
      recognition.lang = 'zh-CN' // 默认中文
      
      recognition.onstart = () => {
        setIsListening(true)
      }
      
      recognition.onend = () => {
        setIsListening(false)
        setInterimTranscript('')
      }
      
      recognition.onresult = (event: SpeechRecognitionEvent) => {
        let finalTranscript = ''
        let interimText = ''
        
        for (let i = event.resultIndex; i < event.results.length; i++) {
          const result = event.results[i]
          if (result.isFinal) {
            finalTranscript += result[0].transcript
          } else {
            interimText += result[0].transcript
          }
        }
        
        if (finalTranscript) {
          setTranscript(prev => prev + finalTranscript)
          onResult?.(finalTranscript)
        }
        setInterimTranscript(interimText)
      }
      
      recognition.onerror = (event: SpeechRecognitionErrorEvent) => {
        setIsListening(false)
        const errorMsg = event.error === 'no-speech' 
          ? '未检测到语音，请重试' 
          : `语音识别错误: ${event.error}`
        onError?.(errorMsg)
      }
      
      recognitionRef.current = recognition
    }
    
    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.abort()
      }
    }
  }, [continuous, interimResults, onResult, onError])
  
  const startListening = useCallback(() => {
    if (!recognitionRef.current) {
      onError?.('当前浏览器不支持语音识别')
      return
    }
    
    try {
      setInterimTranscript('')
      recognitionRef.current.start()
    } catch (err) {
      // 如果已经在运行，忽略错误
      if (err instanceof Error && err.message.includes('already started')) {
        return
      }
      onError?.(err instanceof Error ? err.message : '启动语音识别失败')
    }
  }, [onError])
  
  const stopListening = useCallback(() => {
    if (recognitionRef.current && isListening) {
      recognitionRef.current.stop()
    }
  }, [isListening])
  
  const resetTranscript = useCallback(() => {
    setTranscript('')
    setInterimTranscript('')
  }, [])
  
  return {
    isListening,
    transcript,
    interimTranscript,
    startListening,
    stopListening,
    resetTranscript,
    isSupported: isSupported.current,
  }
}

// 类型声明
declare global {
  interface Window {
    SpeechRecognition: typeof SpeechRecognition
    webkitSpeechRecognition: typeof SpeechRecognition
  }
}

export default useVoiceInput
