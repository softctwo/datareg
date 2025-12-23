import React from 'react'
import ReactECharts from 'echarts-for-react'
import { Card, Button, Space, Dropdown, Menu } from 'antd'
import { DownloadOutlined, ReloadOutlined } from '@ant-design/icons'
import * as echarts from 'echarts'

interface ChartCardProps {
  title: string
  option: any
  height?: number
  loading?: boolean
  onRefresh?: () => void
  onExport?: () => void
  extra?: React.ReactNode
}

/**
 * 增强的图表卡片组件
 * 支持刷新、导出、数据钻取等功能
 */
export const EnhancedChartCard: React.FC<ChartCardProps> = ({
  title,
  option,
  height = 400,
  loading = false,
  onRefresh,
  onExport,
  extra
}) => {
  const chartRef = React.useRef<any>(null)

  const handleExport = () => {
    if (chartRef.current) {
      const chartInstance = chartRef.current.getEchartsInstance()
      const url = chartInstance.getDataURL({
        type: 'png',
        pixelRatio: 2,
        backgroundColor: '#fff'
      })
      const link = document.createElement('a')
      link.download = `${title}_${new Date().getTime()}.png`
      link.href = url
      link.click()
    }
    onExport?.()
  }

  const exportMenu = (
    <Menu>
      <Menu.Item key="png" onClick={handleExport}>
        导出为 PNG
      </Menu.Item>
      <Menu.Item key="refresh" onClick={onRefresh}>
        刷新数据
      </Menu.Item>
    </Menu>
  )

  return (
    <Card
      title={title}
      loading={loading}
      extra={
        <Space>
          {extra}
          {onRefresh && (
            <Button
              type="text"
              icon={<ReloadOutlined />}
              onClick={onRefresh}
              size="small"
            />
          )}
          <Dropdown overlay={exportMenu} trigger={['click']}>
            <Button type="text" icon={<DownloadOutlined />} size="small" />
          </Dropdown>
        </Space>
      }
    >
      <ReactECharts
        ref={chartRef}
        option={option}
        style={{ height: `${height}px`, width: '100%' }}
        opts={{ renderer: 'canvas' }}
        onEvents={{
          click: (params: any) => {
            // 图表点击事件，可用于数据钻取
            console.log('Chart clicked:', params)
          }
        }}
      />
    </Card>
  )
}

/**
 * 热力图组件
 */
export const HeatmapChart: React.FC<{
  data: Array<[string, string, number]>
  xAxisData: string[]
  yAxisData: string[]
  title?: string
  height?: number
}> = ({ data, xAxisData, yAxisData, title = '热力图', height = 400 }) => {
  const option = {
    title: { text: title, left: 'center' },
    tooltip: {
      position: 'top',
      formatter: (params: any) => {
        return `${params.seriesName}<br/>${params.data[0]}: ${params.data[1]}<br/>值: ${params.data[2]}`
      }
    },
    grid: {
      height: '60%',
      top: '15%'
    },
    xAxis: {
      type: 'category',
      data: xAxisData,
      splitArea: {
        show: true
      }
    },
    yAxis: {
      type: 'category',
      data: yAxisData,
      splitArea: {
        show: true
      }
    },
    visualMap: {
      min: 0,
      max: Math.max(...data.map(d => d[2])),
      calculable: true,
      orient: 'horizontal',
      left: 'center',
      bottom: '5%',
      inRange: {
        color: ['#313695', '#4575b4', '#74add1', '#abd9e9', '#e0f3f8', '#ffffcc', '#fee090', '#fdae61', '#f46d43', '#d73027', '#a50026']
      }
    },
    series: [
      {
        name: '操作频率',
        type: 'heatmap',
        data: data,
        label: {
          show: true
        },
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        }
      }
    ]
  }

  return <ReactECharts option={option} style={{ height: `${height}px`, width: '100%' }} />
}

/**
 * 雷达图组件
 */
export const RadarChart: React.FC<{
  data: Array<{ name: string; value: number[] }>
  indicators: Array<{ name: string; max: number }>
  title?: string
  height?: number
}> = ({ data, indicators, title = '雷达图', height = 400 }) => {
  const option = {
    title: { text: title, left: 'center' },
    tooltip: {},
    legend: {
      data: data.map(d => d.name),
      bottom: 0
    },
    radar: {
      indicator: indicators,
      radius: '70%',
      center: ['50%', '50%']
    },
    series: [
      {
        name: '评估维度',
        type: 'radar',
        data: data.map(item => ({
          value: item.value,
          name: item.name,
          areaStyle: {
            opacity: 0.3
          }
        }))
      }
    ]
  }

  return <ReactECharts option={option} style={{ height: `${height}px`, width: '100%' }} />
}

/**
 * 漏斗图组件
 */
export const FunnelChart: React.FC<{
  data: Array<{ name: string; value: number }>
  title?: string
  height?: number
}> = ({ data, title = '漏斗图', height = 400 }) => {
  const option = {
    title: { text: title, left: 'center' },
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} ({d}%)'
    },
    legend: {
      data: data.map(d => d.name),
      bottom: 0
    },
    series: [
      {
        name: '转化率',
        type: 'funnel',
        left: '10%',
        top: 60,
        bottom: 60,
        width: '80%',
        min: 0,
        max: Math.max(...data.map(d => d.value)),
        minSize: '0%',
        maxSize: '100%',
        sort: 'descending',
        gap: 2,
        label: {
          show: true,
          position: 'inside'
        },
        labelLine: {
          length: 10,
          lineStyle: {
            width: 1,
            type: 'solid'
          }
        },
        itemStyle: {
          borderColor: '#fff',
          borderWidth: 1
        },
        emphasis: {
          label: {
            fontSize: 20
          }
        },
        data: data
      }
    ]
  }

  return <ReactECharts option={option} style={{ height: `${height}px`, width: '100%' }} />
}

/**
 * 散点图组件
 */
export const ScatterChart: React.FC<{
  data: Array<[number, number, string?]>
  xAxisName?: string
  yAxisName?: string
  title?: string
  height?: number
}> = ({ data, xAxisName = 'X轴', yAxisName = 'Y轴', title = '散点图', height = 400 }) => {
  const option = {
    title: { text: title, left: 'center' },
    tooltip: {
      trigger: 'item',
      formatter: (params: any) => {
        return `${params.seriesName}<br/>${xAxisName}: ${params.value[0]}<br/>${yAxisName}: ${params.value[1]}`
      }
    },
    xAxis: {
      type: 'value',
      name: xAxisName,
      scale: true
    },
    yAxis: {
      type: 'value',
      name: yAxisName,
      scale: true
    },
    series: [
      {
        name: '数据点',
        type: 'scatter',
        data: data,
        symbolSize: (data: any) => {
          return Math.sqrt(data[2] || 10) * 2
        },
        itemStyle: {
          opacity: 0.6
        },
        emphasis: {
          itemStyle: {
            opacity: 1
          }
        }
      }
    ]
  }

  return <ReactECharts option={option} style={{ height: `${height}px`, width: '100%' }} />
}

/**
 * 桑基图组件（用于数据流向）
 */
export const SankeyChart: React.FC<{
  nodes: Array<{ name: string }>
  links: Array<{ source: string; target: string; value: number }>
  title?: string
  height?: number
}> = ({ nodes, links, title = '数据流向图', height = 400 }) => {
  const option = {
    title: { text: title, left: 'center' },
    tooltip: {
      trigger: 'item',
      triggerOn: 'mousemove'
    },
    series: [
      {
        type: 'sankey',
        data: nodes,
        links: links,
        emphasis: {
          focus: 'adjacency'
        },
        lineStyle: {
          color: 'gradient',
          curveness: 0.5
        }
      }
    ]
  }

  return <ReactECharts option={option} style={{ height: `${height}px`, width: '100%' }} />
}

