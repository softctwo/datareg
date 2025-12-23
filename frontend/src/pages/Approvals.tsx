import React, { useState, useEffect } from 'react'
import {
  Table,
  Button,
  Space,
  Modal,
  Form,
  Select,
  Input,
  message,
  Tag
} from 'antd'
import {
  PlusOutlined,
  CheckOutlined,
  CloseOutlined
} from '@ant-design/icons'
import { approvalsApi, scenariosApi, batchApi } from '../services/api'
import type { ColumnsType } from 'antd/es/table'
import dayjs from 'dayjs'

const { Option } = Select

interface Approval {
  id: number
  scenario_id: number
  approval_status: string
  applicant_id: number
  transfer_type?: string
  transfer_start_time?: string
  transfer_end_time?: string
  actual_volume?: number
  created_at: string
}

const Approvals: React.FC = () => {
  const [data, setData] = useState<Approval[]>([])
  const [scenarios, setScenarios] = useState<any[]>([])
  const [loading, setLoading] = useState(false)
  const [modalVisible, setModalVisible] = useState(false)
  const [selectedRowKeys, setSelectedRowKeys] = useState<React.Key[]>([])
  const [batchModalVisible, setBatchModalVisible] = useState(false)
  const [batchAction, setBatchAction] = useState<'approve' | 'reject' | null>(null)
  const [form] = Form.useForm()

  useEffect(() => {
    loadData()
    loadScenarios()
  }, [])

  const loadData = async () => {
    setLoading(true)
    try {
      const result: any = await approvalsApi.list({})
      setData(Array.isArray(result) ? result : [])
    } catch (error: any) {
      message.error('加载数据失败: ' + (error.message || '未知错误'))
    } finally {
      setLoading(false)
    }
  }

  const loadScenarios = async () => {
    try {
      const result: any = await scenariosApi.list({ status: '已批准' })
      setScenarios(Array.isArray(result) ? result : [])
    } catch (error) {
      console.error('加载场景失败:', error)
    }
  }

  const handleAdd = () => {
    form.resetFields()
    setModalVisible(true)
  }

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields()
      await approvalsApi.create({ ...values, applicant_id: 1 })
      message.success('创建成功')
      setModalVisible(false)
      loadData()
    } catch (error: any) {
      message.error('操作失败: ' + (error.message || '未知错误'))
    }
  }

  const handleApprove = async (id: number) => {
    try {
      await approvalsApi.approve(id, 1, '已批准')
      message.success('批准成功')
      loadData()
    } catch (error: any) {
      message.error('批准失败: ' + (error.message || '未知错误'))
    }
  }

  const handleReject = async (id: number) => {
    Modal.confirm({
      title: '拒绝传输',
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
          await approvalsApi.reject(id, 1, reason)
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
      '待审批': 'processing',
      '已批准': 'success',
      '已拒绝': 'error',
      '已取消': 'default'
    }
    return <Tag color={colorMap[status] || 'default'}>{status}</Tag>
  }

  const columns: ColumnsType<Approval> = [
    {
      title: '场景ID',
      dataIndex: 'scenario_id',
      key: 'scenario_id',
      width: 100
    },
    {
      title: '传输类型',
      dataIndex: 'transfer_type',
      key: 'transfer_type',
      width: 120
    },
    {
      title: '状态',
      dataIndex: 'approval_status',
      key: 'approval_status',
      width: 100,
      render: (status) => getStatusTag(status)
    },
    {
      title: '实际传输量',
      dataIndex: 'actual_volume',
      key: 'actual_volume',
      width: 120,
      render: (volume) => volume ? volume.toLocaleString() : '-'
    },
    {
      title: '传输开始时间',
      dataIndex: 'transfer_start_time',
      key: 'transfer_start_time',
      width: 180,
      render: (time) => time ? dayjs(time).format('YYYY-MM-DD HH:mm:ss') : '-'
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 180,
      render: (time) => dayjs(time).format('YYYY-MM-DD HH:mm:ss')
    },
    {
      title: '操作',
      key: 'action',
      width: 200,
      render: (_, record) => (
        <Space>
          {record.approval_status === '待审批' && (
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
        <h1>传输审批</h1>
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
          <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
            新增审批
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
            disabled: record.approval_status !== '待审批'
          })
        }}
        pagination={{
          showSizeChanger: true,
          showTotal: (total) => `共 ${total} 条`
        }}
      />

      <Modal
        title="新增传输审批"
        open={modalVisible}
        onOk={handleSubmit}
        onCancel={() => setModalVisible(false)}
        width={600}
      >
        <Form form={form} layout="vertical">
          <Form.Item
            name="scenario_id"
            label="关联场景"
            rules={[{ required: true, message: '请选择关联场景' }]}
          >
            <Select placeholder="请选择场景">
              {scenarios.map(s => (
                <Option key={s.id} value={s.id}>
                  {s.scenario_name}
                </Option>
              ))}
            </Select>
          </Form.Item>
          <Form.Item name="transfer_type" label="传输类型">
            <Select placeholder="请选择传输类型">
              <Option value="API">API</Option>
              <Option value="文件">文件</Option>
              <Option value="数据库">数据库</Option>
            </Select>
          </Form.Item>
        </Form>
      </Modal>

      {/* 批量操作弹窗 */}
      <Modal
        title={batchAction === 'approve' ? '批量批准传输' : '批量拒绝传输'}
        open={batchModalVisible}
        onOk={async () => {
          try {
            const userId = 1 // TODO: 从登录用户获取
            if (batchAction === 'approve') {
              const result: any = await batchApi.approveTransfers(selectedRowKeys as number[], userId)
              message.success(`批量批准完成: 成功 ${result.success_count || selectedRowKeys.length} 个，失败 ${result.error_count || 0} 个`)
            } else {
              const reason = form.getFieldValue('batch_reason') || '批量拒绝'
              const result: any = await batchApi.rejectTransfers(selectedRowKeys as number[], userId, reason)
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
          <p>已选择 {selectedRowKeys.length} 个传输审批</p>
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

export default Approvals
