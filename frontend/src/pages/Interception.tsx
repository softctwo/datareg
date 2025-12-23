import React, { useState, useEffect } from 'react'
import {
  Tabs,
  Table,
  Button,
  Space,
  Modal,
  Form,
  Input,
  message,
  Tag,
  Popconfirm,
  Card,
  Alert,
  Select,
  Divider
} from 'antd'
import {
  PlusOutlined,
  DeleteOutlined,
  EyeOutlined,
  SafetyOutlined
} from '@ant-design/icons'
import { interceptionApi, dataAssetsApi } from '../services/api'
import type { ColumnsType } from 'antd/es/table'

const { Option } = Select
const { TextArea } = Input

interface WhitelistEntry {
  approval_id: number
  scenario_id?: number
  scenario_name?: string
  asset_ids: number[]
  added_at?: string
}

interface BlacklistEntry {
  asset_id: number
  asset_name?: string
  asset_code?: string
  data_level?: string
  reason?: string
  added_at?: string
}

interface DataAsset {
  id: number
  asset_name: string
  asset_code: string
  data_level: string
}

const Interception: React.FC = () => {
  const [whitelist, setWhitelist] = useState<WhitelistEntry[]>([])
  const [blacklist, setBlacklist] = useState<BlacklistEntry[]>([])
  const [dataAssets, setDataAssets] = useState<DataAsset[]>([])
  const [loading, setLoading] = useState(false)
  const [blacklistModalVisible, setBlacklistModalVisible] = useState(false)
  const [previewModalVisible, setPreviewModalVisible] = useState(false)
  const [previewData, setPreviewData] = useState<any>(null)
  const [form] = Form.useForm()

  useEffect(() => {
    loadWhitelist()
    loadBlacklist()
    loadDataAssets()
  }, [])

  const loadWhitelist = async () => {
    setLoading(true)
    try {
      const result = await interceptionApi.getWhitelist()
      setWhitelist(Array.isArray(result) ? result : [])
    } catch (error: any) {
      message.error('加载白名单失败: ' + (error.detail || error.message || '未知错误'))
    } finally {
      setLoading(false)
    }
  }

  const loadBlacklist = async () => {
    setLoading(true)
    try {
      const result = await interceptionApi.getBlacklist()
      setBlacklist(Array.isArray(result) ? result : [])
    } catch (error: any) {
      message.error('加载黑名单失败: ' + (error.detail || error.message || '未知错误'))
    } finally {
      setLoading(false)
    }
  }

  const loadDataAssets = async () => {
    try {
      const result = await dataAssetsApi.list({ limit: 1000 })
      setDataAssets(Array.isArray(result) ? result : [])
    } catch (error: any) {
      console.error('加载数据资产失败:', error)
    }
  }

  const handleAddToBlacklist = async () => {
    try {
      const values = await form.validateFields()
      await interceptionApi.addToBlacklist(values.asset_id, values.reason)
      message.success('已添加到黑名单')
      setBlacklistModalVisible(false)
      form.resetFields()
      loadBlacklist()
    } catch (error: any) {
      message.error('添加失败: ' + (error.detail || error.message || '未知错误'))
    }
  }

  const handleRemoveFromBlacklist = async (assetId: number) => {
    try {
      await interceptionApi.removeFromBlacklist(assetId)
      message.success('已从黑名单移除')
      loadBlacklist()
    } catch (error: any) {
      message.error('移除失败: ' + (error.detail || error.message || '未知错误'))
    }
  }

  const handleRemoveFromWhitelist = async (approvalId: number) => {
    try {
      await interceptionApi.removeFromWhitelist(approvalId)
      message.success('已从白名单移除')
      loadWhitelist()
    } catch (error: any) {
      message.error('移除失败: ' + (error.detail || error.message || '未知错误'))
    }
  }

  const handlePreviewDesensitization = async () => {
    try {
      const values = await form.validateFields(['preview_data'])
      const previewData = JSON.parse(values.preview_data || '{}')
      
      const result = await interceptionApi.desensitize({
        data: previewData,
        asset_ids: []
      })
      
      setPreviewData(result)
      setPreviewModalVisible(true)
    } catch (error: any) {
      if (error.message?.includes('JSON')) {
        message.error('请输入有效的JSON数据')
      } else {
        message.error('预览失败: ' + (error.detail || error.message || '未知错误'))
      }
    }
  }

  const whitelistColumns: ColumnsType<WhitelistEntry> = [
    {
      title: '审批ID',
      dataIndex: 'approval_id',
      key: 'approval_id',
      width: 100
    },
    {
      title: '场景名称',
      dataIndex: 'scenario_name',
      key: 'scenario_name',
      width: 200
    },
    {
      title: '数据资产数量',
      dataIndex: 'asset_ids',
      key: 'asset_ids',
      width: 120,
      render: (assetIds: number[]) => assetIds?.length || 0
    },
    {
      title: '添加时间',
      dataIndex: 'added_at',
      key: 'added_at',
      width: 180,
      render: (date: string) => date ? new Date(date).toLocaleString('zh-CN') : '-'
    },
    {
      title: '操作',
      key: 'action',
      width: 150,
      render: (_, record) => (
        <Popconfirm
          title="确定要从白名单移除吗？"
          onConfirm={() => handleRemoveFromWhitelist(record.approval_id)}
        >
          <Button type="link" danger icon={<DeleteOutlined />}>
            移除
          </Button>
        </Popconfirm>
      )
    }
  ]

  const blacklistColumns: ColumnsType<BlacklistEntry> = [
    {
      title: '资产代码',
      dataIndex: 'asset_code',
      key: 'asset_code',
      width: 150
    },
    {
      title: '资产名称',
      dataIndex: 'asset_name',
      key: 'asset_name',
      width: 200
    },
    {
      title: '数据级别',
      dataIndex: 'data_level',
      key: 'data_level',
      width: 120,
      render: (level: string) => {
        const colorMap: Record<string, string> = {
          '核心数据': 'red',
          '重要数据': 'orange',
          '敏感个人信息': 'purple',
          '个人信息': 'blue',
          '内部数据': 'default'
        }
        return <Tag color={colorMap[level || ''] || 'default'}>{level || '-'}</Tag>
      }
    },
    {
      title: '原因',
      dataIndex: 'reason',
      key: 'reason',
      width: 200
    },
    {
      title: '添加时间',
      dataIndex: 'added_at',
      key: 'added_at',
      width: 180,
      render: (date: string) => date ? new Date(date).toLocaleString('zh-CN') : '-'
    },
    {
      title: '操作',
      key: 'action',
      width: 150,
      render: (_, record) => (
        <Popconfirm
          title="确定要从黑名单移除吗？"
          onConfirm={() => handleRemoveFromBlacklist(record.asset_id)}
        >
          <Button type="link" danger icon={<DeleteOutlined />}>
            移除
          </Button>
        </Popconfirm>
      )
    }
  ]

  const tabItems = [
    {
      key: 'whitelist',
      label: '白名单管理',
      children: (
        <div>
          <Alert
            message="白名单说明"
            description="已批准的传输审批会自动添加到白名单。白名单中的传输请求将被允许，但仍需进行脱敏处理。"
            type="info"
            showIcon
            style={{ marginBottom: 16 }}
          />
          <Table
            columns={whitelistColumns}
            dataSource={whitelist}
            rowKey="approval_id"
            loading={loading}
            pagination={{
              showSizeChanger: true,
              showTotal: (total) => `共 ${total} 条`
            }}
          />
        </div>
      )
    },
    {
      key: 'blacklist',
      label: '黑名单管理',
      children: (
        <div>
          <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between' }}>
            <Alert
              message="黑名单说明"
              description="黑名单中的数据资产将被禁止出境，无论是否已获得审批。核心数据会自动拦截，无需加入黑名单。"
              type="warning"
              showIcon
              style={{ flex: 1, marginRight: 16 }}
            />
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={() => setBlacklistModalVisible(true)}
            >
              添加到黑名单
            </Button>
          </div>
          <Table
            columns={blacklistColumns}
            dataSource={blacklist}
            rowKey="asset_id"
            loading={loading}
            pagination={{
              showSizeChanger: true,
              showTotal: (total) => `共 ${total} 条`
            }}
          />
        </div>
      )
    },
    {
      key: 'desensitization',
      label: '脱敏预览',
      children: (
        <div>
          <Card>
            <Alert
              message="脱敏预览"
              description="输入JSON格式的数据，系统将自动识别敏感字段并应用脱敏规则。"
              type="info"
              showIcon
              style={{ marginBottom: 16 }}
            />
            <Form form={form} layout="vertical">
              <Form.Item
                name="preview_data"
                label="输入JSON数据"
                rules={[
                  { required: true, message: '请输入JSON数据' },
                  {
                    validator: (_, value) => {
                      if (!value) return Promise.resolve()
                      try {
                        JSON.parse(value)
                        return Promise.resolve()
                      } catch {
                        return Promise.reject('请输入有效的JSON格式')
                      }
                    }
                  }
                ]}
              >
                <TextArea
                  rows={10}
                  placeholder='{"ID_NO": "110101199001011234", "MOBILE": "13800138000", "CUST_NM": "张三", "EMAIL": "zhangsan@example.com"}'
                  defaultValue={JSON.stringify({
                    "ID_NO": "110101199001011234",
                    "MOBILE": "13800138000",
                    "CUST_NM": "张三",
                    "EMAIL": "zhangsan@example.com",
                    "BANK_CARD": "6222021234567890123",
                    "ADDRESS": "北京市朝阳区xxx街道xxx号"
                  }, null, 2)}
                />
              </Form.Item>
              <Form.Item>
                <Button
                  type="primary"
                  icon={<EyeOutlined />}
                  onClick={handlePreviewDesensitization}
                >
                  预览脱敏效果
                </Button>
              </Form.Item>
            </Form>
          </Card>
        </div>
      )
    }
  ]

  return (
    <div>
      <div style={{ marginBottom: 16 }}>
        <h1>
          <SafetyOutlined style={{ marginRight: 8 }} />
          拦截与脱敏管理
        </h1>
      </div>

      <Tabs items={tabItems} />

      {/* 添加到黑名单弹窗 */}
      <Modal
        title="添加到黑名单"
        open={blacklistModalVisible}
        onOk={handleAddToBlacklist}
        onCancel={() => {
          setBlacklistModalVisible(false)
          form.resetFields()
        }}
        width={600}
      >
        <Form form={form} layout="vertical">
          <Form.Item
            name="asset_id"
            label="选择数据资产"
            rules={[{ required: true, message: '请选择数据资产' }]}
          >
            <Select
              placeholder="请选择数据资产"
              showSearch
              filterOption={(input, option) =>
                (option?.children as unknown as string)?.toLowerCase().includes(input.toLowerCase())
              }
            >
              {dataAssets.map(asset => (
                <Option key={asset.id} value={asset.id}>
                  {asset.asset_code} - {asset.asset_name}
                </Option>
              ))}
            </Select>
          </Form.Item>
          <Form.Item
            name="reason"
            label="原因"
          >
            <TextArea rows={3} placeholder="请输入加入黑名单的原因（可选）" />
          </Form.Item>
        </Form>
      </Modal>

      {/* 脱敏预览弹窗 */}
      <Modal
        title="脱敏效果预览"
        open={previewModalVisible}
        onCancel={() => setPreviewModalVisible(false)}
        footer={null}
        width={800}
      >
        {previewData && (
          <div>
            <Divider orientation="left">原始数据</Divider>
            <pre style={{ background: '#f5f5f5', padding: 16, borderRadius: 4 }}>
              {JSON.stringify(previewData.original_data, null, 2)}
            </pre>
            <Divider orientation="left">脱敏后数据</Divider>
            <pre style={{ background: '#e6f7ff', padding: 16, borderRadius: 4 }}>
              {JSON.stringify(previewData.desensitized_data, null, 2)}
            </pre>
            {previewData.desensitized_fields && previewData.desensitized_fields.length > 0 && (
              <>
                <Divider orientation="left">被脱敏的字段</Divider>
                <Space wrap>
                  {previewData.desensitized_fields.map((field: string) => (
                    <Tag key={field} color="orange">{field}</Tag>
                  ))}
                </Space>
              </>
            )}
          </div>
        )}
      </Modal>
    </div>
  )
}

export default Interception

