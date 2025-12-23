import React, { useState } from 'react'
import {
  Form,
  Input,
  Select,
  DatePicker,
  Button,
  Space,
  Card,
  Row,
  Col,
  Switch
} from 'antd'
import {
  SearchOutlined,
  ReloadOutlined,
  FilterOutlined
} from '@ant-design/icons'
import dayjs from 'dayjs'

const { RangePicker } = DatePicker
const { Option } = Select

export interface AdvancedSearchFilters {
  search?: string
  data_level?: string
  source_system?: string
  asset_name?: string
  asset_code?: string
  asset_type?: string
  is_active?: boolean
  created_from?: string
  created_to?: string
}

interface AdvancedSearchProps {
  onSearch: (filters: AdvancedSearchFilters) => void
  onReset: () => void
  loading?: boolean
  showAdvanced?: boolean
  fields?: string[] // 可配置显示的字段
}

const AdvancedSearch: React.FC<AdvancedSearchProps> = ({
  onSearch,
  onReset,
  loading = false,
  showAdvanced = false,
  fields = ['search', 'data_level', 'source_system', 'asset_type', 'is_active', 'date_range']
}) => {
  const [form] = Form.useForm()
  const [advancedVisible, setAdvancedVisible] = useState(showAdvanced)

  const handleSearch = () => {
    const values = form.getFieldsValue()
    const filters: AdvancedSearchFilters = {}
    
    // 通用搜索
    if (values.search) {
      filters.search = values.search
    }
    
    // 精确搜索
    if (values.asset_name) {
      filters.asset_name = values.asset_name
    }
    if (values.asset_code) {
      filters.asset_code = values.asset_code
    }
    if (values.data_level) {
      filters.data_level = values.data_level
    }
    if (values.source_system) {
      filters.source_system = values.source_system
    }
    if (values.asset_type) {
      filters.asset_type = values.asset_type
    }
    if (values.is_active !== undefined) {
      filters.is_active = values.is_active
    }
    
    // 日期范围
    if (values.date_range && values.date_range.length === 2) {
      filters.created_from = values.date_range[0].format('YYYY-MM-DD HH:mm:ss')
      filters.created_to = values.date_range[1].format('YYYY-MM-DD HH:mm:ss')
    }
    
    onSearch(filters)
  }

  const handleReset = () => {
    form.resetFields()
    onReset()
  }

  return (
    <Card
      size="small"
      style={{ marginBottom: 16 }}
      title={
        <Space>
          <FilterOutlined />
          <span>高级搜索</span>
        </Space>
      }
      extra={
        <Button
          type="link"
          size="small"
          onClick={() => setAdvancedVisible(!advancedVisible)}
        >
          {advancedVisible ? '收起' : '展开'}
        </Button>
      }
    >
      <Form form={form} layout="vertical">
        <Row gutter={16}>
          {/* 通用搜索 */}
          {fields.includes('search') && (
            <Col span={24}>
              <Form.Item name="search" label="通用搜索">
                <Input
                  placeholder="搜索资产名称、编码或描述"
                  allowClear
                  onPressEnter={handleSearch}
                />
              </Form.Item>
            </Col>
          )}

          {/* 基础筛选 */}
          <Col span={fields.includes('data_level') ? 6 : 8}>
            {fields.includes('data_level') && (
              <Form.Item name="data_level" label="数据级别">
                <Select placeholder="全部" allowClear>
                  <Option value="核心数据">核心数据</Option>
                  <Option value="重要数据">重要数据</Option>
                  <Option value="敏感个人信息">敏感个人信息</Option>
                  <Option value="个人信息">个人信息</Option>
                  <Option value="内部数据">内部数据</Option>
                  <Option value="公开数据">公开数据</Option>
                </Select>
              </Form.Item>
            )}
          </Col>

          <Col span={fields.includes('source_system') ? 6 : 8}>
            {fields.includes('source_system') && (
              <Form.Item name="source_system" label="来源系统">
                <Input placeholder="来源系统" allowClear />
              </Form.Item>
            )}
          </Col>

          <Col span={fields.includes('asset_type') ? 6 : 8}>
            {fields.includes('asset_type') && (
              <Form.Item name="asset_type" label="资产类型">
                <Select placeholder="全部" allowClear>
                  <Option value="表">表</Option>
                  <Option value="视图">视图</Option>
                  <Option value="接口">接口</Option>
                  <Option value="文件">文件</Option>
                </Select>
              </Form.Item>
            )}
          </Col>

          <Col span={fields.includes('is_active') ? 6 : 8}>
            {fields.includes('is_active') && (
              <Form.Item name="is_active" label="状态">
                <Select placeholder="全部" allowClear>
                  <Option value={true}>启用</Option>
                  <Option value={false}>禁用</Option>
                </Select>
              </Form.Item>
            )}
          </Col>

          {/* 高级筛选（展开时显示） */}
          {advancedVisible && (
            <>
              <Col span={8}>
                <Form.Item name="asset_name" label="资产名称">
                  <Input placeholder="资产名称" allowClear />
                </Form.Item>
              </Col>
              <Col span={8}>
                <Form.Item name="asset_code" label="资产编码">
                  <Input placeholder="资产编码" allowClear />
                </Form.Item>
              </Col>
              {fields.includes('date_range') && (
                <Col span={8}>
                  <Form.Item name="date_range" label="创建时间">
                    <RangePicker
                      showTime
                      style={{ width: '100%' }}
                      format="YYYY-MM-DD HH:mm:ss"
                    />
                  </Form.Item>
                </Col>
              )}
            </>
          )}
        </Row>

        <Form.Item>
          <Space>
            <Button
              type="primary"
              icon={<SearchOutlined />}
              onClick={handleSearch}
              loading={loading}
            >
              搜索
            </Button>
            <Button
              icon={<ReloadOutlined />}
              onClick={handleReset}
            >
              重置
            </Button>
          </Space>
        </Form.Item>
      </Form>
    </Card>
  )
}

export default AdvancedSearch

