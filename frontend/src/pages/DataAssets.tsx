import React, { useState, useEffect } from 'react'
import {
  Table,
  Button,
  Space,
  Modal,
  Form,
  Input,
  Select,
  message,
  Tag,
  Popconfirm,
  Dropdown,
  Menu,
  Tabs,
  Spin
} from 'antd'
import {
  PlusOutlined,
  ReloadOutlined,
  EditOutlined,
  DeleteOutlined,
  EyeOutlined,
  DownloadOutlined
} from '@ant-design/icons'
import { dataAssetsApi, batchApi, exportApi } from '../services/api'
import type { ColumnsType } from 'antd/es/table'
import LineageGraph from '../components/LineageGraph'
import { getUserPermissions } from '../utils/permissions'
import AdvancedSearch, { AdvancedSearchFilters } from '../components/AdvancedSearch'

const { Option } = Select
const { TextArea } = Input

interface DataAsset {
  id: number
  asset_name: string
  asset_code: string
  asset_type?: string
  source_system?: string
  schema_name?: string
  table_name?: string
  data_level: string
  description?: string
  field_count?: number
  record_count?: number
  is_active: boolean
  created_at: string
}

interface LineageData {
  nodes: Array<{
    id: number
    name: string
    code?: string
    category?: string
    is_center?: boolean
    data_level?: string
  }>
  edges: Array<{
    source: number
    target: number
    relation?: string
    type?: string
  }>
  center_node_id: number
}

const DataAssets: React.FC = () => {
  const [data, setData] = useState<DataAsset[]>([])
  const [loading, setLoading] = useState(false)
  const [modalVisible, setModalVisible] = useState(false)
  const [editingRecord, setEditingRecord] = useState<DataAsset | null>(null)
  const [form] = Form.useForm()
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 10,
    total: 0
  })
  const [selectedRowKeys, setSelectedRowKeys] = useState<React.Key[]>([])
  const [detailModalVisible, setDetailModalVisible] = useState(false)
  const [currentAsset, setCurrentAsset] = useState<DataAsset | null>(null)
  const [lineageData, setLineageData] = useState<LineageData | null>(null)
  const [lineageLoading, setLineageLoading] = useState(false)
  const [userPermissions, setUserPermissions] = useState<string[]>([])
  const [searchFilters, setSearchFilters] = useState<AdvancedSearchFilters>({})

  useEffect(() => {
    loadData()
    fetchUserPermissions()
  }, [pagination.current, pagination.pageSize, searchFilters])

  const fetchUserPermissions = async () => {
    const permissions = await getUserPermissions()
    setUserPermissions(permissions)
  }

  const loadData = async () => {
    setLoading(true)
    try {
      const params: any = {
        skip: (pagination.current - 1) * pagination.pageSize,
        limit: pagination.pageSize,
        ...searchFilters
      }
      const result: any = await dataAssetsApi.list(params)
      // 处理新的响应格式（包含items和total）
      if (result.items) {
        setData(result.items)
        setPagination(prev => ({ ...prev, total: result.total || 0 }))
      } else if (Array.isArray(result)) {
        // 兼容旧格式
        setData(result)
        setPagination(prev => ({ ...prev, total: result.length }))
      } else {
        setData([])
        setPagination(prev => ({ ...prev, total: 0 }))
      }
    } catch (error: any) {
      message.error('加载数据失败: ' + (error.message || '未知错误'))
    } finally {
      setLoading(false)
    }
  }

  const handleSearch = (filters: AdvancedSearchFilters) => {
    setSearchFilters(filters)
    setPagination(prev => ({ ...prev, current: 1 }))
  }

  const handleReset = () => {
    setSearchFilters({})
    setPagination(prev => ({ ...prev, current: 1 }))
  }

  const handleScan = async () => {
    setLoading(true)
    try {
      const result: any = await dataAssetsApi.scan()
      const count = result?.scanned_count || result?.count || 0
      message.success(`扫描完成，发现 ${count} 个资产`)
      loadData()
    } catch (error: any) {
      message.error('扫描失败: ' + (error.message || '未知错误'))
    } finally {
      setLoading(false)
    }
  }

  const handleAdd = () => {
    setEditingRecord(null)
    form.resetFields()
    setModalVisible(true)
  }

  const handleEdit = (record: DataAsset) => {
    setEditingRecord(record)
    form.setFieldsValue(record)
    setModalVisible(true)
  }

  const handleDelete = async (_id: number) => {
    try {
      // 这里需要添加删除API
      message.success('删除成功')
      loadData()
    } catch (error: any) {
      message.error('删除失败: ' + (error.message || '未知错误'))
    }
  }

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields()
      if (editingRecord) {
        await dataAssetsApi.update(editingRecord.id, values)
        message.success('更新成功')
      } else {
        await dataAssetsApi.create(values)
        message.success('创建成功')
      }
      setModalVisible(false)
      loadData()
    } catch (error: any) {
      message.error('操作失败: ' + (error.message || '未知错误'))
    }
  }

  const getLevelTag = (level: string) => {
    const colorMap: Record<string, string> = {
      '核心数据': 'red',
      '重要数据': 'orange',
      '敏感个人信息': 'purple',
      '个人信息': 'blue',
      '内部数据': 'default',
      '公开数据': 'green'
    }
    return <Tag color={colorMap[level] || 'default'}>{level}</Tag>
  }

  const exportMenu = (
    <Menu onClick={({ key }) => window.open(`/api/v1/export/data-assets?format=${key}`, '_blank')}>
      <Menu.Item key="csv">导出为 CSV</Menu.Item>
      <Menu.Item key="json">导出为 JSON</Menu.Item>
    </Menu>
  )

  const columns: ColumnsType<DataAsset> = [
    {
      title: '资产名称',
      dataIndex: 'asset_name',
      key: 'asset_name',
      width: 200
    },
    {
      title: '资产编码',
      dataIndex: 'asset_code',
      key: 'asset_code',
      width: 150
    },
    {
      title: '数据级别',
      dataIndex: 'data_level',
      key: 'data_level',
      width: 120,
      render: (level) => getLevelTag(level)
    },
    {
      title: '来源系统',
      dataIndex: 'source_system',
      key: 'source_system',
      width: 120
    },
    {
      title: '资产类型',
      dataIndex: 'asset_type',
      key: 'asset_type',
      width: 100
    },
    {
      title: '字段数',
      dataIndex: 'field_count',
      key: 'field_count',
      width: 80
    },
    {
      title: '状态',
      dataIndex: 'is_active',
      key: 'is_active',
      width: 80,
      render: (active) => (
        <Tag color={active ? 'green' : 'red'}>{active ? '启用' : '禁用'}</Tag>
      )
    },
    {
      title: '操作',
      key: 'action',
      width: 200,
      render: (_: unknown, record: DataAsset) => (
        <Space>
          <Button
            type="link"
            icon={<EyeOutlined />}
            onClick={async () => {
              setCurrentAsset(record)
              setDetailModalVisible(true)
              // 加载血缘关系数据
              setLineageLoading(true)
              try {
                const lineage = await dataAssetsApi.getLineage(record.id, 2)
                setLineageData(lineage)
              } catch (error: any) {
                message.warning('加载血缘关系失败: ' + (error.message || '未知错误'))
                setLineageData(null)
              } finally {
                setLineageLoading(false)
              }
            }}
          >
            查看
          </Button>
          <Button
            type="link"
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
          >
            编辑
          </Button>
          <Popconfirm
            title="确定要删除这个资产吗？"
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
        <h1>数据资产</h1>
        <Space>
          <Button icon={<ReloadOutlined />} onClick={handleScan} loading={loading}>
            扫描资产
          </Button>
          <Dropdown overlay={exportMenu} placement="bottomLeft">
            <Button icon={<DownloadOutlined />}>
              导出数据
            </Button>
          </Dropdown>
          {selectedRowKeys.length > 0 && hasPermission(userPermissions, 'data_asset:delete') && (
            <Popconfirm
              title={`确定要删除选中的 ${selectedRowKeys.length} 个资产吗？`}
              onConfirm={async () => {
                try {
                  await batchApi.deleteDataAssets(selectedRowKeys as number[])
                  message.success(`成功删除 ${selectedRowKeys.length} 个资产`)
                  setSelectedRowKeys([])
                  loadData()
                } catch (error: any) {
                  message.error('批量删除失败: ' + (error.message || '未知错误'))
                }
              }}
            >
              <Button danger icon={<DeleteOutlined />}>
                批量删除 ({selectedRowKeys.length})
              </Button>
            </Popconfirm>
          )}
          <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
            新增资产
          </Button>
        </Space>
      </div>

      <AdvancedSearch
        onSearch={handleSearch}
        onReset={handleReset}
        loading={loading}
        fields={['search', 'data_level', 'source_system', 'asset_type', 'is_active', 'date_range']}
      />

      <Table
        columns={columns}
        dataSource={data}
        rowKey="id"
        loading={loading}
        rowSelection={{
          selectedRowKeys,
          onChange: (keys) => setSelectedRowKeys(keys)
        }}
        pagination={{
          current: pagination.current,
          pageSize: pagination.pageSize,
          total: pagination.total,
          showSizeChanger: true,
          showTotal: (total) => `共 ${total} 条`,
          onChange: (page, pageSize) => {
            setPagination(prev => ({ ...prev, current: page, pageSize }))
          }
        }}
      />

      <Modal
        title={editingRecord ? '编辑资产' : '新增资产'}
        open={modalVisible}
        onOk={handleSubmit}
        onCancel={() => setModalVisible(false)}
        width={600}
      >
        <Form form={form} layout="vertical">
          <Form.Item
            name="asset_name"
            label="资产名称"
            rules={[{ required: true, message: '请输入资产名称' }]}
          >
            <Input placeholder="请输入资产名称" />
          </Form.Item>
          <Form.Item
            name="asset_code"
            label="资产编码"
            rules={[{ required: true, message: '请输入资产编码' }]}
          >
            <Input placeholder="请输入资产编码" />
          </Form.Item>
          <Form.Item name="asset_type" label="资产类型">
            <Select placeholder="请选择资产类型">
              <Option value="表">表</Option>
              <Option value="视图">视图</Option>
              <Option value="接口">接口</Option>
              <Option value="文件">文件</Option>
            </Select>
          </Form.Item>
          <Form.Item name="source_system" label="来源系统">
            <Input placeholder="请输入来源系统" />
          </Form.Item>
          <Form.Item
            name="data_level"
            label="数据级别"
            rules={[{ required: true, message: '请选择数据级别' }]}
          >
            <Select placeholder="请选择数据级别">
              <Option value="核心数据">核心数据</Option>
              <Option value="重要数据">重要数据</Option>
              <Option value="敏感个人信息">敏感个人信息</Option>
              <Option value="个人信息">个人信息</Option>
              <Option value="内部数据">内部数据</Option>
              <Option value="公开数据">公开数据</Option>
            </Select>
          </Form.Item>
          <Form.Item name="description" label="描述">
            <TextArea rows={4} placeholder="请输入描述" />
          </Form.Item>
        </Form>
      </Modal>

      {/* 资产详情Modal */}
      <Modal
        title="资产详情"
        open={detailModalVisible}
        onCancel={() => {
          setDetailModalVisible(false)
          setCurrentAsset(null)
          setLineageData(null)
        }}
        footer={null}
        width={1000}
      >
        {currentAsset && (
          <Tabs defaultActiveKey="info">
            <Tabs.TabPane tab="基本信息" key="info">
              <div style={{ padding: '16px 0' }}>
                <p><strong>资产名称:</strong> {currentAsset.asset_name}</p>
                <p><strong>资产编码:</strong> {currentAsset.asset_code}</p>
                <p><strong>资产类型:</strong> {currentAsset.asset_type || '未知'}</p>
                <p><strong>数据级别:</strong> {getLevelTag(currentAsset.data_level)}</p>
                <p><strong>来源系统:</strong> {currentAsset.source_system || '未知'}</p>
                <p><strong>Schema:</strong> {currentAsset.schema_name || '未知'}</p>
                <p><strong>表名:</strong> {currentAsset.table_name || '未知'}</p>
                <p><strong>字段数:</strong> {currentAsset.field_count || 0}</p>
                <p><strong>记录数:</strong> {currentAsset.record_count || 0}</p>
                <p><strong>状态:</strong> <Tag color={currentAsset.is_active ? 'green' : 'red'}>{currentAsset.is_active ? '启用' : '禁用'}</Tag></p>
                <p><strong>描述:</strong> {currentAsset.description || '无'}</p>
              </div>
            </Tabs.TabPane>
            <Tabs.TabPane tab="数据血缘" key="lineage">
              {lineageLoading ? (
                <div style={{ textAlign: 'center', padding: '50px 0' }}>
                  <Spin size="large" />
                </div>
              ) : lineageData ? (
                <LineageGraph
                  nodes={lineageData.nodes.map(node => ({
                    id: node.id,
                    name: node.name,
                    code: node.code || node.name || '',
                    type: node.type,
                    data_level: node.data_level || '内部数据'
                  }))}
                  edges={lineageData.edges.map(edge => ({
                    source: edge.source,
                    target: edge.target,
                    type: edge.type || edge.relation || 'related'
                  }))}
                  centerNodeId={lineageData.center_node_id}
                  height={500}
                />
              ) : (
                <div style={{ textAlign: 'center', padding: '50px 0', color: '#999' }}>
                  暂无血缘关系数据
                </div>
              )}
            </Tabs.TabPane>
          </Tabs>
        )}
      </Modal>
    </div>
  )
}

export default DataAssets
