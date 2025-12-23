import React, { useEffect, useState } from 'react'
import { Row, Col, Card, Statistic, Alert, Select, Button, Space, Tag, Tabs } from 'antd'
import { ArrowUpOutlined, ArrowDownOutlined, ReloadOutlined } from '@ant-design/icons'
import { dashboardApi } from '../services/api'
import ReactECharts from 'echarts-for-react'
import { EnhancedChartCard, HeatmapChart, RadarChart, FunnelChart, ScatterChart } from '../components/EnhancedCharts'

const { Option } = Select

const Dashboard: React.FC = () => {
  const [overview, setOverview] = useState<any>(null)
  const [trends, setTrends] = useState<any>(null)
  const [countryDist, setCountryDist] = useState<any>(null)
  const [alerts, setAlerts] = useState<any>(null)
  const [dataAssetStats, setDataAssetStats] = useState<any>(null)
  const [riskStats, setRiskStats] = useState<any>(null)
  const [approvalStats, setApprovalStats] = useState<any>(null)
  const [operationStats, setOperationStats] = useState<any>(null)
  const [heatmapData, setHeatmapData] = useState<any>(null)
  const [funnelData, setFunnelData] = useState<any>(null)
  const [scatterData, setScatterData] = useState<any>(null)
  const [radarData, setRadarData] = useState<any>(null)
  const [trendDays, setTrendDays] = useState(30)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    loadData()
  }, [trendDays])

  const loadData = async () => {
    setLoading(true)
    try {
      const [
        overviewData,
        trendsData,
        countryData,
        alertsData,
        assetData,
        riskData,
        approvalData,
        operationData,
        heatmapDataRes,
        funnelDataRes,
        scatterDataRes,
        radarDataRes
      ] = await Promise.all([
        dashboardApi.getOverview(7),
        dashboardApi.getTransferTrends(trendDays),
        dashboardApi.getCountryDistribution(30),
        dashboardApi.getRiskAlerts(),
        dashboardApi.getDataAssetStatistics(),
        dashboardApi.getRiskStatistics(),
        dashboardApi.getApprovalStatistics(30),
        dashboardApi.getOperationStatistics(7),
        dashboardApi.getHeatmapData(30),
        dashboardApi.getApprovalFunnel(30),
        dashboardApi.getRiskScatter(),
        dashboardApi.getRiskRadar()
      ])
      setOverview(overviewData)
      setTrends(trendsData)
      setCountryDist(countryData)
      setAlerts(alertsData)
      setDataAssetStats(assetData)
      setRiskStats(riskData)
      setApprovalStats(approvalData)
      setOperationStats(operationData)
      setHeatmapData(heatmapDataRes)
      setFunnelData(funnelDataRes)
      setScatterData(scatterDataRes)
      setRadarData(radarDataRes)
    } catch (error: any) {
      console.error('加载数据失败:', error)
      // 如果是401错误，不显示错误信息，让拦截器处理
      if (error.response?.status !== 401) {
        console.error('Dashboard加载错误详情:', error.response?.data || error.message)
      }
    } finally {
      setLoading(false)
    }
  }

  // 传输趋势图表
  const trendOption = {
    title: { text: '传输趋势', left: 'center' },
    tooltip: { trigger: 'axis' },
    legend: { data: ['传输次数', '传输量'], top: 30 },
    grid: { top: 80, left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: {
      type: 'category',
      data: trends?.dates || [],
      boundaryGap: false
    },
    yAxis: [
      {
        type: 'value',
        name: '次数',
        position: 'left'
      },
      {
        type: 'value',
        name: '数据量',
        position: 'right'
      }
    ],
    series: [
      {
        name: '传输次数',
        type: 'line',
        data: trends?.counts || [],
        smooth: true,
        itemStyle: { color: '#1890ff' }
      },
      {
        name: '传输量',
        type: 'bar',
        yAxisIndex: 1,
        data: trends?.volumes || [],
        itemStyle: { color: '#52c41a' }
      }
    ]
  }

  // 目的国分布饼图
  const countryOption = {
    title: { text: '目的国分布', left: 'center' },
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 'left',
      top: 60
    },
    series: [
      {
        name: '传输量',
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: true,
          formatter: '{b}: {c}'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 16,
            fontWeight: 'bold'
          }
        },
        data: countryDist?.countries?.map((country: string, index: number) => ({
          value: countryDist.volumes[index] || 0,
          name: country
        })) || []
      }
    ]
  }

  // 数据资产级别分布
  const assetLevelOption = {
    title: { text: '数据资产级别分布', left: 'center' },
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    xAxis: {
      type: 'category',
      data: dataAssetStats?.level_distribution ? Object.keys(dataAssetStats.level_distribution) : [],
      axisLabel: { rotate: 45 }
    },
    yAxis: { type: 'value' },
    series: [
      {
        name: '资产数量',
        type: 'bar',
        data: dataAssetStats?.level_distribution ? Object.values(dataAssetStats.level_distribution) : [],
        itemStyle: {
          color: (params: any) => {
            const colors: Record<string, string> = {
              '核心数据': '#ff4d4f',
              '重要数据': '#ff9800',
              '敏感个人信息': '#faad14',
              '一般个人信息': '#52c41a',
              '内部数据': '#1890ff',
              '公开数据': '#722ed1'
            }
            return colors[params.name] || '#1890ff'
          }
        }
      }
    ]
  }

  // 风险评估分布
  const riskDistributionOption = {
    title: { text: '风险评估分布', left: 'center' },
    tooltip: { trigger: 'item' },
    legend: {
      orient: 'vertical',
      left: 'left',
      top: 60
    },
    series: [
      {
        name: '风险等级',
        type: 'pie',
        radius: '60%',
        data: riskStats?.risk_distribution ? Object.entries(riskStats.risk_distribution).map(([name, value]) => ({
          value,
          name
        })) : [],
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        }
      }
    ]
  }

  // 审批状态分布
  const approvalStatusOption = {
    title: { text: '审批状态分布', left: 'center' },
    tooltip: { trigger: 'item' },
    series: [
      {
        name: '审批状态',
        type: 'pie',
        radius: ['40%', '70%'],
        data: approvalStats?.status_distribution ? Object.entries(approvalStats.status_distribution).map(([name, value]) => ({
          value,
          name
        })) : [],
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        }
      }
    ]
  }

  // 操作类型统计
  const operationOption = {
    title: { text: '操作类型统计', left: 'center' },
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    xAxis: {
      type: 'category',
      data: operationStats?.actions || [],
      axisLabel: { rotate: 45 }
    },
    yAxis: { type: 'value' },
    series: [
      {
        name: '操作次数',
        type: 'bar',
        data: operationStats?.action_counts || [],
        itemStyle: { color: '#1890ff' }
      }
    ]
  }

  // Top用户操作统计
  const topUsersOption = {
    title: { text: 'Top 10 活跃用户', left: 'center' },
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    xAxis: {
      type: 'value'
    },
    yAxis: {
      type: 'category',
      data: operationStats?.top_users || []
    },
    series: [
      {
        name: '操作次数',
        type: 'bar',
        data: operationStats?.user_counts || [],
        itemStyle: { color: '#52c41a' }
      }
    ]
  }

  return (
    <div>
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h1>监控仪表盘</h1>
        <Space>
          <Select
            value={trendDays}
            onChange={setTrendDays}
            style={{ width: 120 }}
          >
            <Option value={7}>最近7天</Option>
            <Option value={30}>最近30天</Option>
            <Option value={90}>最近90天</Option>
          </Select>
          <Button icon={<ReloadOutlined />} onClick={loadData} loading={loading}>
            刷新
          </Button>
        </Space>
      </div>

      {/* 风险预警 */}
      {alerts && alerts.alerts.length > 0 && (
        <Alert
          message={`发现 ${alerts.total} 个风险预警`}
          description={
            <Space>
              <Tag color="red">严重: {alerts.critical}</Tag>
              <Tag color="orange">高危: {alerts.high}</Tag>
              <Tag color="gold">中危: {alerts.medium}</Tag>
            </Space>
          }
          type="warning"
          showIcon
          style={{ marginBottom: 16 }}
          closable
        />
      )}

      {/* 概览统计卡片 */}
      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="活跃场景"
              value={overview?.scenarios?.active || 0}
              suffix={`/ ${overview?.scenarios?.total || 0}`}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="待审批"
              value={overview?.approvals?.pending || 0}
              valueStyle={{ color: '#cf1322' }}
              prefix={<ArrowUpOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="传输成功率"
              value={overview?.transfers?.success_rate || 0}
              precision={2}
              suffix="%"
              valueStyle={{ color: '#3f8600' }}
              prefix={<ArrowUpOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="异常行为"
              value={overview?.anomalies?.count || 0}
              valueStyle={{ color: '#cf1322' }}
              prefix={<ArrowDownOutlined />}
            />
          </Card>
        </Col>
      </Row>

      {/* 第二行统计卡片 */}
      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="数据资产总数"
              value={dataAssetStats?.total_assets || 0}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="风险评估总数"
              value={riskStats?.total_assessments || 0}
              valueStyle={{ color: '#722ed1' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="总传输量"
              value={overview?.transfers?.total_volume || 0}
              precision={0}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="拦截次数"
              value={overview?.transfers?.intercepted || 0}
              valueStyle={{ color: '#ff4d4f' }}
            />
          </Card>
        </Col>
      </Row>

      {/* 图表区域 */}
      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col span={12}>
          <Card title="传输趋势" loading={loading}>
            {trends && <ReactECharts option={trendOption} style={{ height: 400 }} />}
          </Card>
        </Col>
        <Col span={12}>
          <Card title="目的国分布" loading={loading}>
            {countryDist && <ReactECharts option={countryOption} style={{ height: 400 }} />}
          </Card>
        </Col>
      </Row>

      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col span={12}>
          <Card title="数据资产级别分布" loading={loading}>
            {dataAssetStats && <ReactECharts option={assetLevelOption} style={{ height: 300 }} />}
          </Card>
        </Col>
        <Col span={12}>
          <Card title="风险评估分布" loading={loading}>
            {riskStats && <ReactECharts option={riskDistributionOption} style={{ height: 300 }} />}
          </Card>
        </Col>
      </Row>

      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col span={12}>
          <Card title="审批状态分布" loading={loading}>
            {approvalStats && <ReactECharts option={approvalStatusOption} style={{ height: 300 }} />}
          </Card>
        </Col>
        <Col span={12}>
          <Card title="操作类型统计" loading={loading}>
            {operationStats && <ReactECharts option={operationOption} style={{ height: 300 }} />}
          </Card>
        </Col>
      </Row>

      <Row gutter={16}>
        <Col span={24}>
          <EnhancedChartCard
            title="Top 10 活跃用户"
            option={topUsersOption}
            height={400}
            loading={loading}
            onRefresh={loadData}
          />
        </Col>
      </Row>

      {/* 新增图表区域 */}
      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col span={12}>
          <Card title="操作热力图（操作类型 x 日期）" loading={loading}>
            {heatmapData && (
              <HeatmapChart
                data={heatmapData.data || []}
                xAxisData={heatmapData.xAxis || []}
                yAxisData={heatmapData.yAxis || []}
                title=""
                height={350}
              />
            )}
          </Card>
        </Col>
        <Col span={12}>
          <Card title="审批流程漏斗" loading={loading}>
            {funnelData && (
              <FunnelChart
                data={funnelData.data || []}
                title=""
                height={350}
              />
            )}
          </Card>
        </Col>
      </Row>

      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col span={12}>
          <Card title="风险评估雷达图（多维度）" loading={loading}>
            {radarData && (
              <RadarChart
                data={radarData.data || []}
                indicators={radarData.indicators || []}
                title=""
                height={350}
              />
            )}
          </Card>
        </Col>
        <Col span={12}>
          <Card title="风险评估散点图（数据量 vs 风险等级）" loading={loading}>
            {scatterData && (
              <ScatterChart
                data={scatterData.data || []}
                xAxisName="数据量"
                yAxisName="风险等级"
                title=""
                height={350}
              />
            )}
          </Card>
        </Col>
      </Row>

      {/* 阈值预警详情 */}
      {riskStats && (riskStats.exceeds_personal_threshold > 0 || riskStats.exceeds_sensitive_threshold > 0) && (
        <Card title="阈值预警详情" style={{ marginTop: 16 }}>
          <Row gutter={16}>
            <Col span={12}>
              <Alert
                message="个人信息阈值预警"
                description={`有 ${riskStats.exceeds_personal_threshold} 个评估超过个人信息阈值`}
                type="warning"
                showIcon
              />
            </Col>
            <Col span={12}>
              <Alert
                message="敏感信息阈值预警"
                description={`有 ${riskStats.exceeds_sensitive_threshold} 个评估超过敏感信息阈值`}
                type="error"
                showIcon
              />
            </Col>
          </Row>
        </Card>
      )}
    </div>
  )
}

export default Dashboard
