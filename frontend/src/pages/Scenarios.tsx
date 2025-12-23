import React, { useState, useEffect } from 'react'
import {
  Table,
  Button,
  Space,
  Modal,
  Form,
  Input,
  Select,
  InputNumber,
  message,
  Tag,
  Dropdown
} from 'antd'
import {
  PlusOutlined,
  EditOutlined,
  CheckOutlined,
  CloseOutlined,
  SendOutlined,
  DownloadOutlined
} from '@ant-design/icons'
import { scenariosApi, batchApi } from '../services/api'
import type { ColumnsType } from 'antd/es/table'

const { Option } = Select
const { TextArea } = Input

interface Scenario {
  id: number
  scenario_name: string
  scenario_code: string
  business_type?: string
  recipient_name: string
  recipient_country: string
  recipient_type?: string
  data_purpose: string
  storage_duration?: number
  transfer_frequency?: string
  security_level?: string
  status: string
  created_at: string
}

const Scenarios: React.FC = () => {
  const [data, setData] = useState<Scenario[]>([])
  const [loading, setLoading] = useState(false)
  const [modalVisible, setModalVisible] = useState(false)
  const [editingRecord, setEditingRecord] = useState<Scenario | null>(null)
  const [selectedRowKeys, setSelectedRowKeys] = useState<React.Key[]>([])
  const [batchModalVisible, setBatchModalVisible] = useState(false)
  const [batchAction, setBatchAction] = useState<'approve' | 'reject' | null>(null)
  const [form] = Form.useForm()

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    setLoading(true)
    try {
      const result: any = await scenariosApi.list({})
      setData(Array.isArray(result) ? result : [])
    } catch (error: any) {
      message.error('加载数据失败: ' + (error.message || '未知错误'))
    } finally {
      setLoading(false)
    }
  }

  const handleAdd = () => {
    setEditingRecord(null)
    form.resetFields()
    setModalVisible(true)
  }

  const handleEdit = (record: Scenario) => {
    setEditingRecord(record)
    form.setFieldsValue(record)
    setModalVisible(true)
  }

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields()
      if (editingRecord) {
        await scenariosApi.update(editingRecord.id, values)
        message.success('更新成功')
      } else {
        await scenariosApi.create({ ...values, created_by: 1 }) // TODO: 从登录用户获取
        message.success('创建成功')
      }
      setModalVisible(false)
      loadData()
    } catch (error: any) {
      message.error('操作失败: ' + (error.message || '未知错误'))
    }
  }

  const handleSubmitApproval = async (id: number) => {
    try {
      await scenariosApi.submit(id)
      message.success('提交审批成功')
      loadData()
    } catch (error: any) {
      message.error('提交失败: ' + (error.message || '未知错误'))
    }
  }

  const handleApprove = async (id: number) => {
    try {
      await scenariosApi.approve(id, 1, '已批准') // TODO: 从登录用户获取
      message.success('批准成功')
      loadData()
    } catch (error: any) {
      message.error('批准失败: ' + (error.message || '未知错误'))
    }
  }

  const handleReject = async (id: number) => {
    Modal.confirm({
      title: '拒绝场景',
      content: (
        <Input.TextArea
          placeholder="请输入拒绝原因"
          id="reject-reason"
          rows={4}
        />
      ),
      onOk: async () => {
        const reason = (document.getElementById('reject-reason') as HTMLTextAreaElement)?.value
        if (!reason) {
          message.warning('请输入拒绝原因')
          return
        }
        try {
          await scenariosApi.reject(id, 1, reason)
          message.success('已拒绝')
          loadData()
        } catch (error: any) {
          message.error('操作失败: ' + (error.message || '未知错误'))
        }
      }
    })
  }


  const getStatusTag = (status: string) => {
    const colorMap: Record<string, string> = {
      '草稿': 'default',
      '待审批': 'processing',
      '已批准': 'success',
      '已拒绝': 'error',
      '已过期': 'warning',
      '已暂停': 'warning'
    }
    return <Tag color={colorMap[status] || 'default'}>{status}</Tag>
  }

  const columns: ColumnsType<Scenario> = [
    {
      title: '场景名称',
      dataIndex: 'scenario_name',
      key: 'scenario_name',
      width: 200
    },
    {
      title: '场景编码',
      dataIndex: 'scenario_code',
      key: 'scenario_code',
      width: 150
    },
    {
      title: '业务类型',
      dataIndex: 'business_type',
      key: 'business_type',
      width: 120
    },
    {
      title: '接收方',
      dataIndex: 'recipient_name',
      key: 'recipient_name',
      width: 150
    },
    {
      title: '目的国',
      dataIndex: 'recipient_country',
      key: 'recipient_country',
      width: 100
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status) => getStatusTag(status)
    },
    {
      title: '操作',
      key: 'action',
      width: 300,
      render: (_, record) => (
        <Space>
          {record.status === '草稿' && (
            <>
              <Button
                type="link"
                icon={<EditOutlined />}
                onClick={() => handleEdit(record)}
              >
                编辑
              </Button>
              <Button
                type="link"
                icon={<SendOutlined />}
                onClick={() => handleSubmitApproval(record.id)}
              >
                提交审批
              </Button>
            </>
          )}
          {record.status === '待审批' && (
            <>
              <Button
                type="link"
                icon={<CheckOutlined />}
                onClick={() => handleApprove(record.id)}
              >
                批准
              </Button>
              <Button
                type="link"
                danger
                icon={<CloseOutlined />}
                onClick={() => handleReject(record.id)}
              >
                拒绝
              </Button>
            </>
          )}
        </Space>
      )
    }
  ]

  return (
    <div>
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between' }}>
        <h1>跨境传输场景</h1>
        <Space>
          {selectedRowKeys.length > 0 && (
            <Space>
              <Button
                type="default"
                icon={<CheckOutlined />}
                onClick={() => {
                  setBatchAction('approve')
                  setBatchModalVisible(true)
                }}
              >
                批量批准 ({selectedRowKeys.length})
              </Button>
              <Button
                type="default"
                danger
                icon={<CloseOutlined />}
                onClick={() => {
                  setBatchAction('reject')
                  setBatchModalVisible(true)
                }}
              >
                批量拒绝 ({selectedRowKeys.length})
              </Button>
            </Space>
          )}
          <Dropdown
            menu={{
              items: [
                {
                  key: 'csv',
                  label: '导出为CSV',
                  onClick: async () => {
                    try {
                      const response = await fetch('/api/v1/export/scenarios?format=csv', {
                        headers: {
                          'Authorization': `Bearer ${localStorage.getItem('token')}`
                        }
                      })
                      const blob = await response.blob()
                      const url = window.URL.createObjectURL(blob)
                      const a = document.createElement('a')
                      a.href = url
                      a.download = `scenarios_${new Date().getTime()}.csv`
                      document.body.appendChild(a)
                      a.click()
                      window.URL.revokeObjectURL(url)
                      document.body.removeChild(a)
                      message.success('导出成功')
                    } catch (error: any) {
                      message.error('导出失败: ' + (error.message || '未知错误'))
                    }
                  }
                },
                {
                  key: 'json',
                  label: '导出为JSON',
                  onClick: async () => {
                    try {
                      const response = await fetch('/api/v1/export/scenarios?format=json', {
                        headers: {
                          'Authorization': `Bearer ${localStorage.getItem('token')}`
                        }
                      })
                      const blob = await response.blob()
                      const url = window.URL.createObjectURL(blob)
                      const a = document.createElement('a')
                      a.href = url
                      a.download = `scenarios_${new Date().getTime()}.json`
                      document.body.appendChild(a)
                      a.click()
                      window.URL.revokeObjectURL(url)
                      document.body.removeChild(a)
                      message.success('导出成功')
                    } catch (error: any) {
                      message.error('导出失败: ' + (error.message || '未知错误'))
                    }
                  }
                }
              ]
            }}
          >
            <Button icon={<DownloadOutlined />}>
              导出数据
            </Button>
          </Dropdown>
          <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
            新增场景
          </Button>
        </Space>
      </div>

      <Table
        columns={columns}
        dataSource={data}
        rowKey="id"
        loading={loading}
        rowSelection={{
          selectedRowKeys,
          onChange: (keys) => setSelectedRowKeys(keys),
          getCheckboxProps: (record) => ({
            disabled: record.status !== '待审批'
          })
        }}
        pagination={{
          showSizeChanger: true,
          showTotal: (total) => `共 ${total} 条`
        }}
      />

      <Modal
        title={editingRecord ? '编辑场景' : '新增场景'}
        open={modalVisible}
        onOk={handleSubmit}
        onCancel={() => setModalVisible(false)}
        width={800}
      >
        <Form form={form} layout="vertical">
          <Form.Item
            name="scenario_name"
            label="场景名称"
            rules={[{ required: true, message: '请输入场景名称' }]}
          >
            <Input placeholder="请输入场景名称" />
          </Form.Item>
          <Form.Item
            name="scenario_code"
            label="场景编码"
            rules={[{ required: true, message: '请输入场景编码' }]}
          >
            <Input placeholder="请输入场景编码" />
          </Form.Item>
          <Form.Item name="business_type" label="业务类型">
            <Select placeholder="请选择业务类型">
              <Option value="审计">审计</Option>
              <Option value="合规审查">合规审查</Option>
              <Option value="报表汇总">报表汇总</Option>
              <Option value="其他">其他</Option>
            </Select>
          </Form.Item>
          <Form.Item
            name="recipient_name"
            label="接收方名称"
            rules={[{ required: true, message: '请输入接收方名称' }]}
          >
            <Input placeholder="请输入接收方名称" />
          </Form.Item>
          <Form.Item
            name="recipient_country"
            label="接收方所在国"
            rules={[{ required: true, message: '请输入接收方所在国' }]}
          >
            <Input placeholder="请输入接收方所在国" />
          </Form.Item>
          <Form.Item name="recipient_type" label="接收方类型">
            <Select placeholder="请选择接收方类型">
              <Option value="母行">母行</Option>
              <Option value="境外分行">境外分行</Option>
              <Option value="第三方机构">第三方机构</Option>
            </Select>
          </Form.Item>
          <Form.Item
            name="data_purpose"
            label="数据用途"
            rules={[{ required: true, message: '请输入数据用途' }]}
          >
            <TextArea rows={3} placeholder="请输入数据用途" />
          </Form.Item>
          <Form.Item name="storage_duration" label="存储期限（天）">
            <InputNumber min={0} placeholder="请输入存储期限" style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item name="transfer_frequency" label="传输频率">
            <Select placeholder="请选择传输频率">
              <Option value="实时">实时</Option>
              <Option value="日">日</Option>
              <Option value="周">周</Option>
              <Option value="月">月</Option>
              <Option value="一次性">一次性</Option>
            </Select>
          </Form.Item>
          <Form.Item name="security_level" label="链路安全级别">
            <Select placeholder="请选择安全级别">
              <Option value="高">高</Option>
              <Option value="中">中</Option>
              <Option value="低">低</Option>
            </Select>
          </Form.Item>
        </Form>
      </Modal>

      {/* 批量操作弹窗 */}
      <Modal
        title={batchAction === 'approve' ? '批量批准场景' : '批量拒绝场景'}
        open={batchModalVisible}
        onOk={async () => {
          try {
            const userId = 1 // TODO: 从登录用户获取
            if (batchAction === 'approve') {
              const result: any = await batchApi.approveScenarios(selectedRowKeys as number[], userId)
              message.success(`批量批准完成: 成功 ${result.success_count || selectedRowKeys.length} 个，失败 ${result.error_count || 0} 个`)
            } else {
              const reason = form.getFieldValue('batch_reason') || '批量拒绝'
              const result: any = await batchApi.rejectScenarios(selectedRowKeys as number[], userId, reason)
              message.success(`批量拒绝完成: 成功 ${result.success_count || selectedRowKeys.length} 个，失败 ${result.error_count || 0} 个`)
            }
            setBatchModalVisible(false)
            setSelectedRowKeys([])
            setBatchAction(null)
            loadData()
          } catch (error: any) {
            message.error('批量操作失败: ' + (error.message || '未知错误'))
          }
        }}
        onCancel={() => {
          setBatchModalVisible(false)
          setBatchAction(null)
        }}
      >
        <Form form={form} layout="vertical">
          <p>已选择 {selectedRowKeys.length} 个场景</p>
          {batchAction === 'reject' && (
            <Form.Item
              name="batch_reason"
              label="拒绝原因"
              rules={[{ required: true, message: '请输入拒绝原因' }]}
            >
              <Input.TextArea rows={3} placeholder="请输入拒绝原因" />
            </Form.Item>
          )}
        </Form>
      </Modal>
    </div>
  )
}

export default Scenarios
