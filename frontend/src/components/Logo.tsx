import React from 'react'
import { SafetyOutlined } from '@ant-design/icons'

interface LogoProps {
  collapsed?: boolean
  size?: 'small' | 'medium' | 'large'
}

const Logo: React.FC<LogoProps> = ({ collapsed = false, size = 'medium' }) => {
  const sizeMap = {
    small: { icon: 16, fontSize: 12 },
    medium: { icon: 20, fontSize: 16 },
    large: { icon: 24, fontSize: 20 }
  }
  
  const { icon, fontSize } = sizeMap[size]
  
  if (collapsed) {
    return (
      <div style={{
        height: 40,
        margin: 16,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        color: '#1890ff',
        background: 'rgba(24, 144, 255, 0.1)',
        borderRadius: 8
      }}>
        <SafetyOutlined style={{ fontSize: icon }} />
      </div>
    )
  }
  
  return (
    <div style={{
      height: 40,
      margin: 16,
      display: 'flex',
      alignItems: 'center',
      gap: 8,
      padding: '0 8px',
      background: 'rgba(24, 144, 255, 0.1)',
      borderRadius: 8,
      color: '#1890ff'
    }}>
      <SafetyOutlined style={{ fontSize: icon }} />
      <div style={{ flex: 1, overflow: 'hidden' }}>
        <div style={{ 
          fontSize: fontSize, 
          fontWeight: 'bold',
          lineHeight: 1.2,
          whiteSpace: 'nowrap'
        }}>
          数据管控系统
        </div>
        <div style={{ 
          fontSize: fontSize - 4, 
          color: '#8c8c8c',
          lineHeight: 1.2,
          whiteSpace: 'nowrap'
        }}>
          DataReg
        </div>
      </div>
    </div>
  )
}

export default Logo

