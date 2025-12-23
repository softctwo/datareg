import React, { useState, useEffect } from 'react'
import {
  Table,
  Button,
  Space,
  Modal,
  Form,
  Select,
  message,
  Tag,
  Descriptions
} from 'antd'
import {
  EditOutlined
} from '@ant-design/icons'
import { usersApi, rolesApi } from '../services/api'
import type { ColumnsType } from 'antd/es/table'

const { Option } = Select

interface User {
  id: number
  username: string
  email?: string
  full_name?: string
  is_active: boolean
  is_superuser: boolean
  roles?: Array<{ id: number; name: string }>
}

interface Role {
  id: number
  name: string
  description?: string
}

const UserRoles: React.FC = () => {
  const [users, setUsers] = useState<User[]>([])
  const [roles, setRoles] = useState<Role[]>([])
  const [loading, setLoading] = useState(false)
  const [modalVisible, setModalVisible] = useState(false)
  const [selectedUser, setSelectedUser] = useState<User | null>(null)
  const [form] = Form.useForm()

  useEffect(() => {
    loadUsers()
    loadRoles()
  }, [])

  const loadUsers = async () => {
    setLoading(true)
    try {
      const result = await usersApi.list()
      setUsers(Array.isArray(result) ? result : [])
    } catch (error: any) {
      message.error('加载用户失败: ' + (error.detail || error.message || '未知错误'))
    } finally {
      setLoading(false)
    }
  }

  const loadRoles = async () => {
    try {
      const result = await rolesApi.list()
      setRoles(Array.isArray(result) ? result : [])
    } catch (error: any) {
      message.error('加载角色失败: ' + (error.detail || error.message || '未知错误'))
    }
  }

  const handleAssignRoles = (user: User) => {
    setSelectedUser(user)
    form.setFieldsValue({
      role_ids: user.roles?.map(r => r.id) || []
    })
    setModalVisible(true)
  }

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields()
      
      if (!selectedUser?.id) {
        message.error('请选择用户')
        return
      }
      
      await rolesApi.assign(selectedUser.id, values.role_ids || [])
      
      message.success('角色分配成功')
      setModalVisible(false)
      loadUsers()
    } catch (error: any) {
      message.error('分配失败: ' + (error.detail || error.message || '未知错误'))
    }
  }

  const columns: ColumnsType<User> = [
    {
      title: '用户名',
      dataIndex: 'username',
      key: 'username',
      width: 150
    },
    {
      title: '邮箱',
      dataIndex: 'email',
      key: 'email',
      width: 200
    },
    {
      title: '姓名',
      dataIndex: 'full_name',
      key: 'full_name',
      width: 150
    },
    {
      title: '角色',
      dataIndex: 'roles',
      key: 'roles',
      render: (roles: Array<{ id: number; name: string }>) => (
        <Space wrap>
          {roles && roles.length > 0 ? (
            roles.map(r => (
              <Tag key={r.id} color="blue">{r.name}</Tag>
            ))
          ) : (
            <Tag>无角色</Tag>
          )}
        </Space>
      )
    },
    {
      title: '状态',
      dataIndex: 'is_active',
      key: 'is_active',
      width: 100,
      render: (isActive: boolean) => (
        <Tag color={isActive ? 'green' : 'red'}>
          {isActive ? '启用' : '禁用'}
        </Tag>
      )
    },
    {
      title: '超级用户',
      dataIndex: 'is_superuser',
      key: 'is_superuser',
      width: 100,
      render: (isSuperuser: boolean) => (
        isSuperuser ? <Tag color="purple">是</Tag> : <Tag>否</Tag>
      )
    },
    {
      title: '操作',
      key: 'action',
      width: 150,
      render: (_, record) => (
        <Button
          type="link"
          icon={<EditOutlined />}
          onClick={() => handleAssignRoles(record)}
        >
          分配角色
        </Button>
      )
    }
  ]

  return (
    <div>
      <div style={{ marginBottom: 16 }}>
        <h1>用户角色分配</h1>
      </div>

      <Table
        columns={columns}
        dataSource={users}
        rowKey="id"
        loading={loading}
        pagination={{
          showSizeChanger: true,
          showTotal: (total) => `共 ${total} 条`
        }}
      />

      <Modal
        title="分配角色"
        open={modalVisible}
        onOk={handleSubmit}
        onCancel={() => setModalVisible(false)}
        width={600}
      >
        {selectedUser && (
          <Descriptions column={1} style={{ marginBottom: 16 }}>
            <Descriptions.Item label="用户名">{selectedUser.username}</Descriptions.Item>
            <Descriptions.Item label="邮箱">{selectedUser.email || '-'}</Descriptions.Item>
            <Descriptions.Item label="姓名">{selectedUser.full_name || '-'}</Descriptions.Item>
          </Descriptions>
        )}
        
        <Form form={form} layout="vertical">
          <Form.Item
            name="role_ids"
            label="角色"
            rules={[{ required: false }]}
          >
            <Select
              mode="multiple"
              placeholder="请选择角色（可多选）"
              style={{ width: '100%' }}
              showSearch
              allowClear
              filterOption={(input, option) =>
                (option?.children as unknown as string)?.toLowerCase().includes(input.toLowerCase())
              }
            >
              {roles.map(role => (
                <Option key={role.id} value={role.id}>
                  {role.name}{role.description ? ` - ${role.description}` : ''}
                </Option>
              ))}
            </Select>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}

export default UserRoles

