import React, { useState, useEffect } from 'react'
import {
  Table,
  Button,
  Space,
  Modal,
  Form,
  Input,
  message,
  Tag,
  Popconfirm,
  Switch
} from 'antd'
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  UserOutlined
} from '@ant-design/icons'
import { usersApi } from '../services/api'
import type { ColumnsType } from 'antd/es/table'

interface User {
  id: number
  username: string
  email?: string
  full_name?: string
  is_active: boolean
  is_superuser: boolean
  roles?: Array<{ id: number; name: string }>
  created_at: string
}

const Users: React.FC = () => {
  const [data, setData] = useState<User[]>([])
  const [loading, setLoading] = useState(false)
  const [modalVisible, setModalVisible] = useState(false)
  const [editingRecord, setEditingRecord] = useState<User | null>(null)
  const [form] = Form.useForm()

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    setLoading(true)
    try {
      const result = await usersApi.list()
      setData(Array.isArray(result) ? result : [])
    } catch (error: any) {
      message.error('加载数据失败: ' + (error.detail || error.message || '未知错误'))
    } finally {
      setLoading(false)
    }
  }

  const handleAdd = () => {
    setEditingRecord(null)
    form.resetFields()
    form.setFieldsValue({
      is_active: true,
      is_superuser: false
    })
    setModalVisible(true)
  }

  const handleEdit = (record: User) => {
    setEditingRecord(record)
    form.setFieldsValue({
      username: record.username,
      email: record.email,
      full_name: record.full_name,
      is_active: record.is_active,
      is_superuser: record.is_superuser,
      password: '' // 密码留空，不修改则不更新
    })
    setModalVisible(true)
  }

  const handleDelete = async (id: number) => {
    try {
      await usersApi.delete(id)
      message.success('删除成功')
      loadData()
    } catch (error: any) {
      message.error('删除失败: ' + (error.detail || error.message || '未知错误'))
    }
  }

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields()
      
      if (editingRecord) {
        // 更新用户
        const updateData: any = {
          email: values.email,
          full_name: values.full_name,
          is_active: values.is_active,
          is_superuser: values.is_superuser
        }
        // 只有填写了密码才更新
        if (values.password && values.password.trim()) {
          updateData.password = values.password
        }
        await usersApi.update(editingRecord.id, updateData)
        message.success('更新成功')
      } else {
        // 创建用户
        await usersApi.create({
          username: values.username,
          email: values.email,
          full_name: values.full_name,
          password: values.password,
          is_active: values.is_active !== false,
          is_superuser: values.is_superuser === true
        })
        message.success('创建成功')
      }
      setModalVisible(false)
      loadData()
    } catch (error: any) {
      message.error('操作失败: ' + (error.detail || error.message || '未知错误'))
    }
  }

  const handleToggleActive = async (record: User) => {
    try {
      await usersApi.update(record.id, {
        is_active: !record.is_active
      })
      message.success(record.is_active ? '用户已禁用' : '用户已启用')
      loadData()
    } catch (error: any) {
      message.error('操作失败: ' + (error.detail || error.message || '未知错误'))
    }
  }

  const columns: ColumnsType<User> = [
    {
      title: '用户名',
      dataIndex: 'username',
      key: 'username',
      width: 150,
      fixed: 'left'
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
      width: 200,
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
      render: (isActive: boolean, record: User) => (
        <Switch
          checked={isActive}
          onChange={() => handleToggleActive(record)}
          checkedChildren="启用"
          unCheckedChildren="禁用"
        />
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
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 180,
      render: (date: string) => date ? new Date(date).toLocaleString('zh-CN') : '-'
    },
    {
      title: '操作',
      key: 'action',
      width: 200,
      fixed: 'right',
      render: (_, record) => (
        <Space>
          <Button
            type="link"
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
          >
            编辑
          </Button>
          <Popconfirm
            title="确定要删除这个用户吗？"
            onConfirm={() => handleDelete(record.id)}
            okText="确定"
            cancelText="取消"
          >
            <Button type="link" danger icon={<DeleteOutlined />}>
              删除
            </Button>
          </Popconfirm>
        </Space>
      )
    }
  ]

  return (
    <div>
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between' }}>
        <h1>用户管理</h1>
        <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
          新增用户
        </Button>
      </div>

      <Table
        columns={columns}
        dataSource={data}
        rowKey="id"
        loading={loading}
        scroll={{ x: 1200 }}
        pagination={{
          showSizeChanger: true,
          showTotal: (total) => `共 ${total} 条`
        }}
      />

      <Modal
        title={editingRecord ? '编辑用户' : '新增用户'}
        open={modalVisible}
        onOk={handleSubmit}
        onCancel={() => setModalVisible(false)}
        width={600}
        okText="确定"
        cancelText="取消"
      >
        <Form form={form} layout="vertical">
          <Form.Item
            name="username"
            label="用户名"
            rules={[
              { required: !editingRecord, message: '请输入用户名' },
              { min: 3, message: '用户名至少3个字符' },
              { max: 50, message: '用户名最多50个字符' }
            ]}
          >
            <Input 
              placeholder="请输入用户名" 
              disabled={!!editingRecord}
              prefix={<UserOutlined />}
            />
          </Form.Item>
          
          <Form.Item
            name="email"
            label="邮箱"
            rules={[
              { type: 'email', message: '请输入有效的邮箱地址' }
            ]}
          >
            <Input placeholder="请输入邮箱" />
          </Form.Item>
          
          <Form.Item
            name="full_name"
            label="姓名"
          >
            <Input placeholder="请输入姓名" />
          </Form.Item>
          
          <Form.Item
            name="password"
            label={editingRecord ? '新密码（留空则不修改）' : '密码'}
            rules={[
              { required: !editingRecord, message: '请输入密码' },
              { min: 6, message: '密码至少6个字符' }
            ]}
          >
            <Input.Password placeholder={editingRecord ? '留空则不修改密码' : '请输入密码'} />
          </Form.Item>
          
          <Form.Item
            name="is_active"
            label="状态"
            valuePropName="checked"
          >
            <Switch checkedChildren="启用" unCheckedChildren="禁用" />
          </Form.Item>
          
          <Form.Item
            name="is_superuser"
            label="超级用户"
            valuePropName="checked"
          >
            <Switch checkedChildren="是" unCheckedChildren="否" />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}

export default Users

