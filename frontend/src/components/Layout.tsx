import React, { useState } from 'react'
import { Layout, Menu, theme, Button, Dropdown } from 'antd'
import {
  DashboardOutlined,
  DatabaseOutlined,
  GlobalOutlined,
  SafetyOutlined,
  FileTextOutlined,
  AuditOutlined,
  LogoutOutlined,
  UserOutlined,
  TeamOutlined,
  BellOutlined,
  SettingOutlined
} from '@ant-design/icons'
import { useNavigate, useLocation } from 'react-router-dom'
import Logo from './Logo'

const { Header, Sider, Content } = Layout

interface AppLayoutProps {
  children: React.ReactNode
}

const AppLayout: React.FC<AppLayoutProps> = ({ children }) => {
  const [collapsed, setCollapsed] = useState(false)
  const navigate = useNavigate()
  const location = useLocation()
  const {
    token: { colorBgContainer },
  } = theme.useToken()

  const menuItems = [
    {
      key: '/',
      icon: <DashboardOutlined />,
      label: '监控仪表盘',
    },
    {
      key: '/data-assets',
      icon: <DatabaseOutlined />,
      label: '数据资产',
    },
    {
      key: '/scenarios',
      icon: <GlobalOutlined />,
      label: '跨境场景',
    },
    {
      key: '/risk-assessments',
      icon: <SafetyOutlined />,
      label: '风险评估',
    },
    {
      key: '/approvals',
      icon: <FileTextOutlined />,
      label: '传输审批',
    },
    {
      key: '/audit-logs',
      icon: <AuditOutlined />,
      label: '审计日志',
    },
    {
      key: '/roles',
      icon: <TeamOutlined />,
      label: '角色管理',
    },
    {
      key: '/users',
      icon: <UserOutlined />,
      label: '用户管理',
    },
    {
      key: '/user-roles',
      icon: <UserOutlined />,
      label: '用户角色分配',
    },
    {
      key: '/interception',
      icon: <SafetyOutlined />,
      label: '拦截与脱敏',
      permission: 'interception:read'
    },
    {
      key: '/notifications',
      icon: <BellOutlined />,
      label: '通知中心',
      permission: 'notification:read'
    },
    {
      key: '/system-config',
      icon: <SettingOutlined />,
      label: '系统配置',
      permission: 'config:read'
    },
  ]

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider 
        trigger={null} 
        collapsible 
        collapsed={collapsed}
        onCollapse={setCollapsed}
        width={200}
      >
        <Logo collapsed={collapsed} size="medium" />
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[location.pathname]}
          items={menuItems}
          onClick={({ key }) => navigate(key)}
        />
      </Sider>
      <Layout>
        <Header style={{ 
          padding: 0, 
          background: colorBgContainer, 
          display: 'flex', 
          justifyContent: 'space-between', 
          alignItems: 'center',
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
        }}>
          <div style={{ 
            padding: '0 24px', 
            fontSize: 18, 
            fontWeight: 'bold',
            color: '#1890ff',
            display: 'flex',
            alignItems: 'center',
            gap: 12
          }}>
            <SafetyOutlined style={{ fontSize: 24 }} />
            <span>银行重要数据跨境数据管控系统</span>
          </div>
          <div style={{ padding: '0 24px' }}>
            <Dropdown
              menu={{
                items: [
                  {
                    key: 'logout',
                    icon: <LogoutOutlined />,
                    label: '退出登录',
                    onClick: () => {
                      localStorage.removeItem('token')
                      navigate('/login')
                    }
                  }
                ]
              }}
            >
              <Button type="text" icon={<UserOutlined />}>
                用户
              </Button>
            </Dropdown>
          </div>
        </Header>
        <Content
          style={{
            margin: '24px 16px',
            padding: 24,
            minHeight: 280,
            background: colorBgContainer,
          }}
        >
          {children}
        </Content>
      </Layout>
    </Layout>
  )
}

export default AppLayout

