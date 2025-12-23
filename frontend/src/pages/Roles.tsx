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
  Checkbox
} from 'antd'
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined
} from '@ant-design/icons'
import axios from 'axios'
import type { ColumnsType } from 'antd/es/table'

const { TextArea } = Input

interface Role {
  id: number
  name: string
  description?: string
  permissions?: string[]
  created_at: string
}

import { PERMISSIONS_BY_GROUP } from '../utils/permissions'

const Roles: React.FC = () => {
  const [data, setData] = useState<Role[]>([])
  const [loading, setLoading] = useState(false)
  const [modalVisible, setModalVisible] = useState(false)
  const [editingRecord, setEditingRecord] = useState<Role | null>(null)
  const [form] = Form.useForm()

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    setLoading(true)
    try {
      const token = localStorage.getItem('token')
      const response = await axios.get('/api/v1/roles', {
        headers: { Authorization: `Bearer ${token}` }
      })
      setData(response.data || [])
    } catch (error: any) {
      message.error('加载数据失败: ' + (error.response?.data?.detail || '未知错误'))
    } finally {
      setLoading(false)
    }
  }

  const handleAdd = () => {
    setEditingRecord(null)
    form.resetFields()
    setModalVisible(true)
  }

  const handleEdit = (record: Role) => {
    setEditingRecord(record)
    form.setFieldsValue({
      ...record,
      permissions: record.permissions || []
    })
    setModalVisible(true)
  }

  const handleDelete = async (id: number) => {
    try {
      const token = localStorage.getItem('token')
      await axios.delete(`/api/v1/roles/${id}`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      message.success('删除成功')
      loadData()
    } catch (error: any) {
      message.error('删除失败: ' + (error.response?.data?.detail || '未知错误'))
    }
  }

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields()
      const token = localStorage.getItem('token')
      
      if (editingRecord) {
        await axios.put(`/api/v1/roles/${editingRecord.id}`, values, {
          headers: { Authorization: `Bearer ${token}` }
        })
        message.success('更新成功')
      } else {
        await axios.post('/api/v1/roles', values, {
          headers: { Authorization: `Bearer ${token}` }
        })
        message.success('创建成功')
      }
      setModalVisible(false)
      loadData()
    } catch (error: any) {
      message.error('操作失败: ' + (error.response?.data?.detail || '未知错误'))
    }
  }

  const columns: ColumnsType<Role> = [
    {
      title: '角色名称',
      dataIndex: 'name',
      key: 'name',
      width: 150
    },
    {
      title: '描述',
      dataIndex: 'description',
      key: 'description',
      width: 200
    },
    {
      title: '权限',
      dataIndex: 'permissions',
      key: 'permissions',
      render: (permissions: string[]) => (
        <Space wrap>
          {permissions && permissions.length > 0 ? (
            permissions.slice(0, 3).map(p => (
              <Tag key={p}>{p}</Tag>
            ))
          ) : (
            <Tag>无权限</Tag>
          )}
          {permissions && permissions.length > 3 && (
            <Tag>+{permissions.length - 3}</Tag>
          )}
        </Space>
      )
    },
    {
      title: '操作',
      key: 'action',
      width: 200,
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
            title="确定要删除这个角色吗？"
            onConfirm={() => handleDelete(record.id)}
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
        <h1>角色管理</h1>
        <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
          新增角色
        </Button>
      </div>

      <Table
        columns={columns}
        dataSource={data}
        rowKey="id"
        loading={loading}
        pagination={{
          showSizeChanger: true,
          showTotal: (total) => `共 ${total} 条`
        }}
      />

      <Modal
        title={editingRecord ? '编辑角色' : '新增角色'}
        open={modalVisible}
        onOk={handleSubmit}
        onCancel={() => setModalVisible(false)}
        width={600}
      >
        <Form form={form} layout="vertical">
          <Form.Item
            name="name"
            label="角色名称"
            rules={[{ required: true, message: '请输入角色名称' }]}
          >
            <Input placeholder="请输入角色名称" />
          </Form.Item>
          <Form.Item name="description" label="描述">
            <TextArea rows={3} placeholder="请输入描述" />
          </Form.Item>
          <Form.Item name="permissions" label="权限">
            <Checkbox.Group style={{ width: '100%' }}>
              {Object.entries(PERMISSIONS_BY_GROUP).map(([group, perms]) => (
                <div key={group} style={{ marginBottom: 16 }}>
                  <div style={{ fontWeight: 'bold', marginBottom: 8, color: '#1890ff' }}>
                    {group}
                  </div>
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '8px', marginLeft: 16 }}>
                    {perms.map(p => (
                      <Checkbox key={p.value} value={p.value}>
                        {p.label}
                      </Checkbox>
                    ))}
                  </div>
                </div>
              ))}
            </Checkbox.Group>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}

export default Roles

