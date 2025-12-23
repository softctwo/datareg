import React, { useState } from 'react'
import { Form, Input, Button, message } from 'antd'
import { UserOutlined, LockOutlined, SafetyOutlined } from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'

const Login: React.FC = () => {
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()
  const [form] = Form.useForm()

  const handleSubmit = async (values: { username: string; password: string }) => {
    setLoading(true)
    try {
      const formData = new FormData()
      formData.append('username', values.username)
      formData.append('password', values.password)

      const response = await axios.post('/api/v1/auth/login', formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      })

      const { access_token } = response.data
      localStorage.setItem('token', access_token)
      message.success('登录成功')
      navigate('/')
    } catch (error: any) {
      message.error('登录失败: ' + (error.response?.data?.detail || '未知错误'))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{
      display: 'flex',
      minHeight: '100vh',
      background: '#f5f7fa'
    }}>
      {/* 左侧品牌区域 */}
      <div style={{
        flex: 1,
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
        background: 'linear-gradient(135deg, #1890ff 0%, #096dd9 100%)',
        color: 'white',
        padding: '60px 80px',
        position: 'relative',
        overflow: 'hidden'
      }}>
        {/* 背景装饰 */}
        <div style={{
          position: 'absolute',
          top: -100,
          right: -100,
          width: 400,
          height: 400,
          borderRadius: '50%',
          background: 'rgba(255, 255, 255, 0.1)',
          filter: 'blur(60px)'
        }} />
        <div style={{
          position: 'absolute',
          bottom: -150,
          left: -150,
          width: 500,
          height: 500,
          borderRadius: '50%',
          background: 'rgba(255, 255, 255, 0.08)',
          filter: 'blur(80px)'
        }} />
        
        {/* Logo和标题 */}
        <div style={{
          position: 'relative',
          zIndex: 1,
          textAlign: 'center',
          maxWidth: 500
        }}>
          <div style={{
            width: 80,
            height: 80,
            margin: '0 auto 32px',
            borderRadius: '20px',
            background: 'rgba(255, 255, 255, 0.2)',
            backdropFilter: 'blur(10px)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)',
            border: '1px solid rgba(255, 255, 255, 0.3)'
          }}>
            <SafetyOutlined style={{ fontSize: 40, color: 'white' }} />
          </div>
          <h1 style={{
            fontSize: 36,
            fontWeight: 600,
            margin: '0 0 16px',
            letterSpacing: '-0.5px'
          }}>
            数据管控系统
          </h1>
          <p style={{
            fontSize: 18,
            margin: '0 0 8px',
            opacity: 0.95,
            fontWeight: 300
          }}>
            银行重要数据跨境数据管控平台
          </p>
          <p style={{
            fontSize: 14,
            margin: 0,
            opacity: 0.8,
            fontWeight: 300
          }}>
            DataReg - 安全 · 合规 · 高效
          </p>
        </div>
      </div>

      {/* 右侧登录表单区域 */}
      <div style={{
        width: 480,
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        padding: '60px 60px',
        background: 'white'
      }}>
        <div style={{ marginBottom: 48 }}>
          <h2 style={{
            fontSize: 28,
            fontWeight: 600,
            margin: '0 0 8px',
            color: '#1f2937',
            letterSpacing: '-0.5px'
          }}>
            欢迎登录
          </h2>
          <p style={{
            fontSize: 14,
            color: '#6b7280',
            margin: 0
          }}>
            请输入您的账号和密码以继续
          </p>
        </div>

        <Form
          form={form}
          name="login"
          onFinish={handleSubmit}
          layout="vertical"
          size="large"
          autoComplete="off"
        >
          <Form.Item
            name="username"
            rules={[{ required: true, message: '请输入用户名' }]}
            style={{ marginBottom: 24 }}
          >
            <Input
              prefix={<UserOutlined style={{ color: '#9ca3af' }} />}
              placeholder="用户名"
              style={{
                height: 48,
                borderRadius: 8,
                border: '1px solid #e5e7eb',
                fontSize: 14
              }}
            />
          </Form.Item>
          
          <Form.Item
            name="password"
            rules={[{ required: true, message: '请输入密码' }]}
            style={{ marginBottom: 32 }}
          >
            <Input.Password
              prefix={<LockOutlined style={{ color: '#9ca3af' }} />}
              placeholder="密码"
              style={{
                height: 48,
                borderRadius: 8,
                border: '1px solid #e5e7eb',
                fontSize: 14
              }}
            />
          </Form.Item>
          
          <Form.Item style={{ marginBottom: 0 }}>
            <Button
              type="primary"
              htmlType="submit"
              block
              loading={loading}
              style={{
                height: 48,
                borderRadius: 8,
                fontSize: 16,
                fontWeight: 500,
                background: '#1890ff',
                border: 'none',
                boxShadow: '0 2px 8px rgba(24, 144, 255, 0.3)'
              }}
            >
              {loading ? '登录中...' : '登录'}
            </Button>
          </Form.Item>
        </Form>

        <div style={{
          marginTop: 32,
          paddingTop: 24,
          borderTop: '1px solid #f3f4f6',
          textAlign: 'center'
        }}>
          <p style={{
            fontSize: 12,
            color: '#9ca3af',
            margin: 0
          }}>
            © 2024 数据管控系统 DataReg. 保留所有权利
          </p>
        </div>
      </div>
    </div>
  )
}

export default Login
