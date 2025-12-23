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
  Alert,
  Descriptions
} from 'antd'
import {
  PlusOutlined,
  CalculatorOutlined,
  WarningOutlined,
  EyeOutlined
} from '@ant-design/icons'
import { riskAssessmentsApi, scenariosApi } from '../services/api'
import type { ColumnsType } from 'antd/es/table'

const { Option } = Select

interface RiskAssessment {
  id: number
  assessment_name: string
  assessment_code: string
  assessment_type: string
  scenario_id: number
  legal_environment_score?: number
  data_volume_score?: number
  security_measures_score?: number
  data_sensitivity_score?: number
  personal_info_count?: number
  sensitive_info_count?: number
  exceeds_personal_threshold: boolean
  exceeds_sensitive_threshold: boolean
  overall_risk_level?: string
  overall_score?: number
  status: string
  requires_regulatory_approval: boolean
}

const RiskAssessments: React.FC = () => {
  const [data, setData] = useState<RiskAssessment[]>([])
  const [scenarios, setScenarios] = useState<any[]>([])
  const [loading, setLoading] = useState(false)
  const [modalVisible, setModalVisible] = useState(false)
  const [detailVisible, setDetailVisible] = useState(false)
  const [selectedRecord, setSelectedRecord] = useState<RiskAssessment | null>(null)
  const [thresholdCheck, setThresholdCheck] = useState<any>(null)
  const [form] = Form.useForm()

  useEffect(() => {
    loadData()
    loadScenarios()
  }, [])

  const loadData = async () => {
    setLoading(true)
    try {
      const result: any = await riskAssessmentsApi.list({})
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
      await riskAssessmentsApi.create({ ...values, assessor_id: 1 })
      message.success('创建成功')
      setModalVisible(false)
      loadData()
    } catch (error: any) {
      message.error('操作失败: ' + (error.message || '未知错误'))
    }
  }

  const handleCalculate = async (id: number) => {
    try {
      await riskAssessmentsApi.calculate(id)
      message.success('评估计算完成')
      loadData()
    } catch (error: any) {
      message.error('计算失败: ' + (error.message || '未知错误'))
    }
  }

  const handleCheckThresholds = async (record: RiskAssessment) => {
    try {
      const result = await riskAssessmentsApi.checkThresholds(record.id)
      setThresholdCheck(result)
      setSelectedRecord(record)
      setDetailVisible(true)
    } catch (error: any) {
      message.error('检查失败: ' + (error.message || '未知错误'))
    }
  }

  const getRiskLevelTag = (level?: string) => {
    if (!level) return <Tag>未评估</Tag>
    // 处理可能的Enum格式
    const levelStr = typeof level === 'string' ? level : String(level)
    const levelValue = levelStr.includes('.') ? levelStr.split('.').pop() || levelStr : levelStr
    const colorMap: Record<string, string> = {
      '低风险': 'green',
      'LOW': 'green',
      '中风险': 'blue',
      'MEDIUM': 'blue',
      '高风险': 'orange',
      'HIGH': 'orange',
      '极高风险': 'red',
      'CRITICAL': 'red'
    }
    return <Tag color={colorMap[levelValue] || 'default'}>{levelValue}</Tag>
  }

  const columns: ColumnsType<RiskAssessment> = [
    {
      title: '评估名称',
      dataIndex: 'assessment_name',
      key: 'assessment_name',
      width: 200
    },
    {
      title: '评估编码',
      dataIndex: 'assessment_code',
      key: 'assessment_code',
      width: 150
    },
    {
      title: '评估类型',
      dataIndex: 'assessment_type',
      key: 'assessment_type',
      width: 100
    },
    {
      title: '风险等级',
      dataIndex: 'overall_risk_level',
      key: 'overall_risk_level',
      width: 120,
      render: (level) => getRiskLevelTag(level)
    },
    {
      title: '综合评分',
      dataIndex: 'overall_score',
      key: 'overall_score',
      width: 100,
      render: (score: number | string | null) => {
        if (!score) return '-'
        const numScore = typeof score === 'string' ? parseFloat(score) : score
        return isNaN(numScore) ? '-' : numScore.toFixed(2)
      }
    },
    {
      title: '阈值检查',
      key: 'threshold',
      width: 150,
      render: (_, record) => (
        <Space>
          {record.exceeds_personal_threshold && (
            <Tag color="red">个人信息超阈值</Tag>
          )}
          {record.exceeds_sensitive_threshold && (
            <Tag color="red">敏感信息超阈值</Tag>
          )}
        </Space>
      )
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status: string) => {
        // 处理可能的Enum格式
        const statusStr = typeof status === 'string' ? status : String(status)
        // 如果包含点号，取最后一部分
        const statusValue = statusStr.includes('.') ? statusStr.split('.').pop() || statusStr : statusStr
        const colorMap: Record<string, string> = {
          '草稿': 'default',
          'DRAFT': 'default',
          '进行中': 'processing',
          'IN_PROGRESS': 'processing',
          '已完成': 'success',
          'COMPLETED': 'success',
          '已归档': 'default',
          'ARCHIVED': 'default'
        }
        return <Tag color={colorMap[statusValue] || 'default'}>{statusValue}</Tag>
      }
    },
    {
      title: '操作',
      key: 'action',
      width: 250,
      render: (_, record) => (
        <Space>
          <Button
            type="link"
            icon={<EyeOutlined />}
            onClick={() => {
              setSelectedRecord(record)
              setDetailVisible(true)
            }}
          >
            详情
          </Button>
          {(record.status === '草稿' || record.status === 'DRAFT' || String(record.status).includes('DRAFT')) && (
            <Button
              type="link"
              icon={<CalculatorOutlined />}
              onClick={() => handleCalculate(record.id)}
            >
              计算
            </Button>
          )}
          <Button
            type="link"
            icon={<WarningOutlined />}
            onClick={() => handleCheckThresholds(record)}
          >
            阈值检查
          </Button>
        </Space>
      )
    }
  ]

  return (
    <div>
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between' }}>
        <h1>风险评估</h1>
        <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
          新增评估
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
        title="新增风险评估"
        open={modalVisible}
        onOk={handleSubmit}
        onCancel={() => setModalVisible(false)}
        width={600}
      >
        <Form form={form} layout="vertical">
          <Form.Item
            name="assessment_name"
            label="评估名称"
            rules={[{ required: true, message: '请输入评估名称' }]}
          >
            <Input placeholder="请输入评估名称" />
          </Form.Item>
          <Form.Item
            name="assessment_code"
            label="评估编码"
            rules={[{ required: true, message: '请输入评估编码' }]}
          >
            <Input placeholder="请输入评估编码" />
          </Form.Item>
          <Form.Item
            name="assessment_type"
            label="评估类型"
            initialValue="PIA"
          >
            <Select>
              <Option value="PIA">PIA</Option>
              <Option value="DPIA">DPIA</Option>
            </Select>
          </Form.Item>
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
          <Form.Item name="legal_environment_score" label="法律环境评分 (0-100)">
            <InputNumber min={0} max={100} style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item name="data_volume_score" label="数据规模评分 (0-100)">
            <InputNumber min={0} max={100} style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item name="security_measures_score" label="安全措施评分 (0-100)">
            <InputNumber min={0} max={100} style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item name="data_sensitivity_score" label="数据敏感性评分 (0-100)">
            <InputNumber min={0} max={100} style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item name="personal_info_count" label="个人信息数量">
            <InputNumber min={0} style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item name="sensitive_info_count" label="敏感个人信息数量">
            <InputNumber min={0} style={{ width: '100%' }} />
          </Form.Item>
        </Form>
      </Modal>

      <Modal
        title="评估详情"
        open={detailVisible}
        onCancel={() => {
          setDetailVisible(false)
          setThresholdCheck(null)
        }}
        footer={null}
        width={800}
      >
        {selectedRecord && (
          <div>
            <Descriptions column={2} bordered>
              <Descriptions.Item label="评估名称">{selectedRecord.assessment_name}</Descriptions.Item>
              <Descriptions.Item label="评估编码">{selectedRecord.assessment_code}</Descriptions.Item>
              <Descriptions.Item label="风险等级">
                {getRiskLevelTag(selectedRecord.overall_risk_level)}
              </Descriptions.Item>
              <Descriptions.Item label="综合评分">
                {selectedRecord.overall_score ? 
                  (typeof selectedRecord.overall_score === 'string' ? 
                    parseFloat(selectedRecord.overall_score).toFixed(2) : 
                    Number(selectedRecord.overall_score).toFixed(2)) : 
                  '-'}
              </Descriptions.Item>
              <Descriptions.Item label="个人信息数量">
                {selectedRecord.personal_info_count || 0}
              </Descriptions.Item>
              <Descriptions.Item label="敏感信息数量">
                {selectedRecord.sensitive_info_count || 0}
              </Descriptions.Item>
              <Descriptions.Item label="需要监管审批" span={2}>
                {selectedRecord.requires_regulatory_approval ? (
                  <Tag color="red">是</Tag>
                ) : (
                  <Tag color="green">否</Tag>
                )}
              </Descriptions.Item>
            </Descriptions>

            {thresholdCheck && thresholdCheck.warnings && thresholdCheck.warnings.length > 0 && (
              <div style={{ marginTop: 16 }}>
                <Alert
                  message="阈值预警"
                  description={
                    <ul>
                      {thresholdCheck.warnings.map((w: any, index: number) => (
                        <li key={index}>
                          <strong>{w.type}:</strong> {w.message} ({w.level})
                        </li>
                      ))}
                    </ul>
                  }
                  type="warning"
                  showIcon
                />
              </div>
            )}
          </div>
        )}
      </Modal>
    </div>
  )
}

export default RiskAssessments
