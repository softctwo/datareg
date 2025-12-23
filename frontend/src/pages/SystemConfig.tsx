import React, { useState, useEffect } from 'react'
import {
  Table,
  Button,
  Space,
  Modal,
  Form,
  Input,
  Select,
  Switch,
  message,
  Tag,
  Popconfirm,
  Tabs,
  Card,
  InputNumber,
  Tooltip,
  Alert
} from 'antd'
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  ReloadOutlined,
  SettingOutlined,
  SearchOutlined,
  ExportOutlined,
  EyeOutlined,
  CopyOutlined
} from '@ant-design/icons'
import { systemConfigApi } from '../services/api'
import type { ColumnsType } from 'antd/es/table'
import { getUserPermissions, hasPermission } from '../utils/permissions'
import dayjs from 'dayjs'

const { Option } = Select
const { TextArea } = Input

interface SystemConfig {
  id: number
  config_key: string
  config_name: string
  config_value: string
  config_type: string
  category: string
  description?: string
  is_encrypted: boolean
  is_editable: boolean
  is_public: boolean
  default_value?: string
  updated_by?: number
  created_at: string
  updated_at?: string
}

const SystemConfig: React.FC = () => {
  const [data, setData] = useState<SystemConfig[]>([])
  const [filteredData, setFilteredData] = useState<SystemConfig[]>([])
  const [loading, setLoading] = useState(false)
  const [modalVisible, setModalVisible] = useState(false)
  const [detailModalVisible, setDetailModalVisible] = useState(false)
  const [editingRecord, setEditingRecord] = useState<SystemConfig | null>(null)
  const [detailRecord, setDetailRecord] = useState<SystemConfig | null>(null)
  const [form] = Form.useForm()
  const [activeTab, setActiveTab] = useState<string>('all')
  const [userPermissions, setUserPermissions] = useState<string[]>([])
  const [searchText, setSearchText] = useState<string>('')

  const fetchUserPermissions = async () => {
    const permissions = await getUserPermissions()
    setUserPermissions(permissions)
  }

  const filterData = (configs: SystemConfig[], search: string) => {
    if (!search.trim()) {
      setFilteredData(configs)
      return
    }
    const filtered = configs.filter(config => 
      config.config_key.toLowerCase().includes(search.toLowerCase()) ||
      config.config_name.toLowerCase().includes(search.toLowerCase()) ||
      (config.description && config.description.toLowerCase().includes(search.toLowerCase())) ||
      config.config_value.toLowerCase().includes(search.toLowerCase())
    )
    setFilteredData(filtered)
  }

  const loadData = async () => {
    setLoading(true)
    try {
      const params: any = {}
      if (activeTab !== 'all') {
        params.category = activeTab
      }
      const result = await systemConfigApi.list(params)
      const configs = Array.isArray(result) ? result : []
      setData(configs)
      filterData(configs, searchText)
    } catch (error: any) {
      // 401/403错误会被拦截器处理，这里只处理其他错误
      const status = error.response?.status || error.status
      if (status !== 401 && status !== 403) {
        message.error('加载配置失败: ' + (error.detail || error.message || '未知错误'))
      } else if (status === 403) {
        message.error('权限不足，无法访问系统配置')
      }
      setData([])
      setFilteredData([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadData()
    fetchUserPermissions()
  }, [activeTab])

  useEffect(() => {
    filterData(data, searchText)
  }, [searchText, data])

  const handleAdd = () => {
    setEditingRecord(null)
    form.resetFields()
    setModalVisible(true)
  }

  const handleEdit = (record: SystemConfig) => {
    setEditingRecord(record)
    form.setFieldsValue({
      ...record,
      config_value: record.config_value
    })
    setModalVisible(true)
  }

  const handleViewDetail = (record: SystemConfig) => {
    setDetailRecord(record)
    setDetailModalVisible(true)
  }

  const handleCopyValue = (value: string) => {
    navigator.clipboard.writeText(value)
    message.success('已复制到剪贴板')
  }

  const handleExport = () => {
    try {
      const exportData = data.map(config => ({
        config_key: config.config_key,
        config_name: config.config_name,
        config_value: config.config_value,
        config_type: config.config_type,
        category: config.category,
        description: config.description,
        is_editable: config.is_editable,
        is_public: config.is_public
      }))
      const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `system_config_${new Date().toISOString().split('T')[0]}.json`
      a.click()
      URL.revokeObjectURL(url)
      message.success('导出成功')
    } catch (error: any) {
      message.error('导出失败: ' + (error.message || '未知错误'))
    }
  }

  const handleDelete = async (id: number) => {
    try {
      await systemConfigApi.delete(id)
      message.success('删除成功')
      loadData()
    } catch (error: any) {
      message.error('删除失败: ' + (error.message || '未知错误'))
    }
  }

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields()
      
      // 类型转换
      if (values.config_type === 'integer' || values.config_type === 'float') {
        values.config_value = String(values.config_value)
      } else if (values.config_type === 'boolean') {
        values.config_value = String(values.config_value).toLowerCase()
      }
      
      if (editingRecord) {
        await systemConfigApi.update(editingRecord.id, {
          config_value: values.config_value,
          description: values.description,
          is_editable: values.is_editable,
          is_public: values.is_public
        })
        message.success('更新成功')
      } else {
        await systemConfigApi.create(values)
        message.success('创建成功')
      }
      setModalVisible(false)
      form.resetFields()
      loadData()
    } catch (error: any) {
      if (error.errorFields) {
        // 表单验证错误
        return
      }
      message.error('操作失败: ' + (error.message || error.detail || '未知错误'))
    }
  }

  const getCategoryTag = (category: string) => {
    const colorMap: Record<string, string> = {
      '阈值配置': 'red',
      '脱敏规则': 'orange',
      '审批流程': 'blue',
      '通知设置': 'green',
      '系统设置': 'purple',
      '合规规则': 'cyan'
    }
    return <Tag color={colorMap[category] || 'default'}>{category}</Tag>
  }

  const getTypeTag = (type: string) => {
    const colorMap: Record<string, string> = {
      'string': 'blue',
      'integer': 'green',
      'float': 'orange',
      'boolean': 'purple',
      'json': 'cyan'
    }
    return <Tag color={colorMap[type] || 'default'}>{type}</Tag>
  }

  const columns: ColumnsType<SystemConfig> = [
    {
      title: '配置键',
      dataIndex: 'config_key',
      key: 'config_key',
      width: 200,
      fixed: 'left',
      render: (text, record) => (
        <Tooltip title={text}>
          <span style={{ cursor: 'pointer' }} onClick={() => handleViewDetail(record)}>
            {text}
          </span>
        </Tooltip>
      )
    },
    {
      title: '配置名称',
      dataIndex: 'config_name',
      key: 'config_name',
      width: 200
    },
    {
      title: '配置值',
      dataIndex: 'config_value',
      key: 'config_value',
      width: 200,
      ellipsis: true,
      render: (value, record) => (
        record.is_encrypted ? '***' : (value?.length > 50 ? value.substring(0, 50) + '...' : value)
      )
    },
    {
      title: '类型',
      dataIndex: 'config_type',
      key: 'config_type',
      width: 100,
      render: (type) => getTypeTag(type)
    },
    {
      title: '分类',
      dataIndex: 'category',
      key: 'category',
      width: 120,
      render: (category) => getCategoryTag(category)
    },
    {
      title: '可编辑',
      dataIndex: 'is_editable',
      key: 'is_editable',
      width: 80,
      render: (editable) => (
        <Tag color={editable ? 'green' : 'red'}>{editable ? '是' : '否'}</Tag>
      )
    },
    {
      title: '公开',
      dataIndex: 'is_public',
      key: 'is_public',
      width: 80,
      render: (isPublic) => (
        <Tag color={isPublic ? 'blue' : 'default'}>{isPublic ? '是' : '否'}</Tag>
      )
    },
    {
      title: '描述',
      dataIndex: 'description',
      key: 'description',
      ellipsis: true
    },
    {
      title: '更新时间',
      dataIndex: 'updated_at',
      key: 'updated_at',
      width: 180,
      render: (time) => time ? dayjs(time).format('YYYY-MM-DD HH:mm:ss') : '-'
    },
    {
      title: '操作',
      key: 'action',
      width: 200,
      fixed: 'right',
      render: (_, record) => (
        <Space>
          <Tooltip title="查看详情">
            <Button
              type="link"
              icon={<EyeOutlined />}
              onClick={() => handleViewDetail(record)}
            />
          </Tooltip>
          {hasPermission(userPermissions, 'config:write') && record.is_editable && (
            <Tooltip title="编辑">
              <Button
                type="link"
                icon={<EditOutlined />}
                onClick={() => handleEdit(record)}
              />
            </Tooltip>
          )}
          {hasPermission(userPermissions, 'config:delete') && record.is_editable && (
            <Popconfirm
              title="确定要删除这个配置吗？"
              onConfirm={() => handleDelete(record.id)}
            >
              <Tooltip title="删除">
                <Button type="link" danger icon={<DeleteOutlined />} />
              </Tooltip>
            </Popconfirm>
          )}
        </Space>
      )
    }
  ]

  const categoryTabs = [
    { key: 'all', label: '全部' },
    { key: '阈值配置', label: '阈值配置' },
    { key: '脱敏规则', label: '脱敏规则' },
    { key: '审批流程', label: '审批流程' },
    { key: '通知设置', label: '通知设置' },
    { key: '系统设置', label: '系统设置' },
    { key: '合规规则', label: '合规规则' }
  ]

  return (
    <div>
      <div style={{ marginBottom: 16 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
          <h1>系统配置管理</h1>
          <Space>
            <Button icon={<ReloadOutlined />} onClick={loadData} loading={loading}>
              刷新
            </Button>
            <Button icon={<ExportOutlined />} onClick={handleExport}>
              导出配置
            </Button>
            {hasPermission(userPermissions, 'config:write') && (
              <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
                新增配置
              </Button>
            )}
          </Space>
        </div>
        <Input
          placeholder="搜索配置键、配置名称、描述或配置值..."
          prefix={<SearchOutlined />}
          value={searchText}
          onChange={(e) => setSearchText(e.target.value)}
          allowClear
          style={{ width: 400 }}
        />
      </div>

      <Card>
        <Tabs activeKey={activeTab} onChange={setActiveTab} items={categoryTabs.map(tab => ({
          key: tab.key,
          label: tab.label
        }))} />

        <Table
          columns={columns}
          dataSource={filteredData.length > 0 ? filteredData : data}
          rowKey="id"
          loading={loading}
          scroll={{ x: 1500 }}
          pagination={{
            showSizeChanger: true,
            showTotal: (total) => `共 ${total} 条${searchText ? `（搜索: ${searchText}）` : ''}`
          }}
        />
      </Card>

      <Modal
        title={editingRecord ? '编辑配置' : '新增配置'}
        open={modalVisible}
        onOk={handleSubmit}
        onCancel={() => setModalVisible(false)}
        width={700}
      >
        <Form form={form} layout="vertical">
          {!editingRecord && (
            <>
              <Form.Item
                name="config_key"
                label="配置键"
                rules={[
                  { required: true, message: '请输入配置键' },
                  { pattern: /^[a-z0-9_.]+$/, message: '配置键只能包含小写字母、数字、下划线和点' }
                ]}
              >
                <Input placeholder="例如: threshold.personal_info.max" />
              </Form.Item>
              <Form.Item
                name="config_name"
                label="配置名称"
                rules={[{ required: true, message: '请输入配置名称' }]}
              >
                <Input placeholder="例如: 个人信息最大数量" />
              </Form.Item>
              <Form.Item
                name="category"
                label="配置分类"
                rules={[{ required: true, message: '请选择配置分类' }]}
              >
                <Select placeholder="请选择配置分类">
                  <Option value="阈值配置">阈值配置</Option>
                  <Option value="脱敏规则">脱敏规则</Option>
                  <Option value="审批流程">审批流程</Option>
                  <Option value="通知设置">通知设置</Option>
                  <Option value="系统设置">系统设置</Option>
                  <Option value="合规规则">合规规则</Option>
                </Select>
              </Form.Item>
              <Form.Item
                name="config_type"
                label="配置类型"
                rules={[{ required: true, message: '请选择配置类型' }]}
              >
                <Select placeholder="请选择配置类型">
                  <Option value="string">字符串 (string)</Option>
                  <Option value="integer">整数 (integer)</Option>
                  <Option value="float">浮点数 (float)</Option>
                  <Option value="boolean">布尔值 (boolean)</Option>
                  <Option value="json">JSON (json)</Option>
                </Select>
              </Form.Item>
              <Form.Item name="is_encrypted" label="加密存储" valuePropName="checked">
                <Switch />
              </Form.Item>
              <Form.Item name="is_editable" label="可编辑" valuePropName="checked" initialValue={true}>
                <Switch />
              </Form.Item>
              <Form.Item name="is_public" label="公开（前端可访问）" valuePropName="checked">
                <Switch />
              </Form.Item>
              <Form.Item name="default_value" label="默认值">
                <Input placeholder="配置的默认值（可选）" />
              </Form.Item>
            </>
          )}
          <Form.Item
            name="config_value"
            label="配置值"
            rules={[
              { required: true, message: '请输入配置值' },
              ({ getFieldValue }) => ({
                validator(_, value) {
                  if (!value) return Promise.resolve()
                  const configType = editingRecord ? editingRecord.config_type : getFieldValue('config_type')
                  
                  // 根据类型验证
                  if (configType === 'integer') {
                    if (!/^-?\d+$/.test(value)) {
                      return Promise.reject(new Error('请输入有效的整数'))
                    }
                  } else if (configType === 'float') {
                    if (!/^-?\d+(\.\d+)?$/.test(value)) {
                      return Promise.reject(new Error('请输入有效的浮点数'))
                    }
                  } else if (configType === 'boolean') {
                    if (!['true', 'false', '1', '0', 'yes', 'no'].includes(value.toLowerCase())) {
                      return Promise.reject(new Error('请输入有效的布尔值（true/false）'))
                    }
                  } else if (configType === 'json') {
                    try {
                      JSON.parse(value)
                    } catch {
                      return Promise.reject(new Error('请输入有效的JSON格式'))
                    }
                  }
                  return Promise.resolve()
                }
              })
            ]}
          >
            {editingRecord && editingRecord.config_type === 'integer' ? (
              <InputNumber style={{ width: '100%' }} placeholder="请输入整数" />
            ) : editingRecord && editingRecord.config_type === 'float' ? (
              <InputNumber style={{ width: '100%' }} step={0.01} placeholder="请输入浮点数" />
            ) : editingRecord && editingRecord.config_type === 'boolean' ? (
              <Select placeholder="请选择布尔值">
                <Option value="true">true</Option>
                <Option value="false">false</Option>
              </Select>
            ) : (
              <TextArea 
                rows={4} 
                placeholder="请输入配置值（JSON类型请使用JSON格式，布尔值请输入true/false）" 
              />
            )}
          </Form.Item>
          <Form.Item name="description" label="描述">
            <TextArea rows={3} placeholder="请输入配置描述" />
          </Form.Item>
          {editingRecord && (
            <>
              <Form.Item name="is_editable" label="可编辑" valuePropName="checked">
                <Switch />
              </Form.Item>
              <Form.Item name="is_public" label="公开（前端可访问）" valuePropName="checked">
                <Switch />
              </Form.Item>
            </>
          )}
        </Form>
      </Modal>

      <Modal
        title="配置详情"
        open={detailModalVisible}
        onCancel={() => setDetailModalVisible(false)}
        footer={[
          <Button key="copy" icon={<CopyOutlined />} onClick={() => detailRecord && handleCopyValue(detailRecord.config_value)}>
            复制值
          </Button>,
          <Button key="close" onClick={() => setDetailModalVisible(false)}>
            关闭
          </Button>
        ]}
        width={800}
      >
        {detailRecord && (
          <div>
            <Alert
              message="配置详情"
              description="查看配置的完整信息，包括配置值、描述等"
              type="info"
              showIcon
              style={{ marginBottom: 16 }}
            />
            <Form layout="vertical">
              <Form.Item label="配置键">
                <Input value={detailRecord.config_key} readOnly />
              </Form.Item>
              <Form.Item label="配置名称">
                <Input value={detailRecord.config_name} readOnly />
              </Form.Item>
              <Form.Item label="配置值">
                <TextArea 
                  rows={detailRecord.config_type === 'json' ? 10 : 4} 
                  value={detailRecord.config_value} 
                  readOnly
                  style={{ fontFamily: detailRecord.config_type === 'json' ? 'monospace' : 'inherit' }}
                />
              </Form.Item>
              <Form.Item label="配置类型">
                {getTypeTag(detailRecord.config_type)}
              </Form.Item>
              <Form.Item label="配置分类">
                {getCategoryTag(detailRecord.category)}
              </Form.Item>
              {detailRecord.description && (
                <Form.Item label="描述">
                  <TextArea rows={3} value={detailRecord.description} readOnly />
                </Form.Item>
              )}
              <Form.Item label="属性">
                <Space>
                  <Tag color={detailRecord.is_editable ? 'green' : 'red'}>
                    {detailRecord.is_editable ? '可编辑' : '不可编辑'}
                  </Tag>
                  <Tag color={detailRecord.is_public ? 'blue' : 'default'}>
                    {detailRecord.is_public ? '公开' : '私有'}
                  </Tag>
                  <Tag color={detailRecord.is_encrypted ? 'orange' : 'default'}>
                    {detailRecord.is_encrypted ? '已加密' : '未加密'}
                  </Tag>
                </Space>
              </Form.Item>
              {detailRecord.default_value && (
                <Form.Item label="默认值">
                  <Input value={detailRecord.default_value} readOnly />
                </Form.Item>
              )}
              <Form.Item label="创建时间">
                <Input value={dayjs(detailRecord.created_at).format('YYYY-MM-DD HH:mm:ss')} readOnly />
              </Form.Item>
              {detailRecord.updated_at && (
                <Form.Item label="更新时间">
                  <Input value={dayjs(detailRecord.updated_at).format('YYYY-MM-DD HH:mm:ss')} readOnly />
                </Form.Item>
              )}
            </Form>
          </div>
        )}
      </Modal>
    </div>
  )
}

export default SystemConfig

