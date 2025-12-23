import React, { useEffect, useRef } from 'react'
import * as echarts from 'echarts'
import { Card, Spin, message } from 'antd'

interface LineageNode {
  id: number
  name: string
  code: string
  type?: string
  data_level: string
}

interface LineageEdge {
  source: number
  target: number
  type: string
}

interface LineageGraphProps {
  nodes: LineageNode[]
  edges: LineageEdge[]
  centerNodeId: number
  height?: number
}

const LineageGraph: React.FC<LineageGraphProps> = ({
  nodes,
  edges,
  centerNodeId,
  height = 600
}) => {
  const chartRef = useRef<HTMLDivElement>(null)
  const chartInstance = useRef<echarts.ECharts | null>(null)

  useEffect(() => {
    if (!chartRef.current) return

    // 初始化图表
    if (!chartInstance.current) {
      chartInstance.current = echarts.init(chartRef.current)
    }

    const chart = chartInstance.current

    // 数据级别颜色映射
    const levelColors: Record<string, string> = {
      '核心数据': '#ff4d4f',
      '重要数据': '#ff7a45',
      '敏感个人信息': '#ff7875',
      '个人信息': '#ffc53d',
      '内部数据': '#40a9ff',
      '公开数据': '#73d13d'
    }

    // 转换节点数据
    const graphNodes = nodes.map(node => ({
      id: node.id.toString(),
      name: node.name,
      value: node.id === centerNodeId ? 1 : 0.5,
      category: node.data_level,
      symbolSize: node.id === centerNodeId ? 50 : 30,
      itemStyle: {
        color: levelColors[node.data_level] || '#40a9ff',
        borderColor: node.id === centerNodeId ? '#1890ff' : '#d9d9d9',
        borderWidth: node.id === centerNodeId ? 3 : 1
      },
      label: {
        show: true,
        fontSize: 12,
        fontWeight: node.id === centerNodeId ? 'bold' : 'normal'
      },
      tooltip: {
        formatter: (params: any) => {
          const node = nodes.find(n => n.id === parseInt(params.data.id))
          if (!node) return ''
          return `
            <div>
              <strong>${node.name}</strong><br/>
              编码: ${node.code}<br/>
              类型: ${node.type || '未知'}<br/>
              级别: ${node.data_level}
            </div>
          `
        }
      }
    }))

    // 转换边数据
    const graphLinks = edges.map(edge => ({
      source: edge.source.toString(),
      target: edge.target.toString(),
      lineStyle: {
        color: edge.type === 'downstream' ? '#1890ff' : '#52c41a',
        width: 2,
        curveness: 0.3
      },
      label: {
        show: false
      }
    }))

    // 配置选项
    const option: echarts.EChartsOption = {
      title: {
        text: '数据血缘关系图',
        left: 'center',
        textStyle: {
          fontSize: 16,
          fontWeight: 'bold'
        }
      },
      tooltip: {
        trigger: 'item',
        formatter: (params: any) => {
          if (params.dataType === 'node') {
            const node = nodes.find(n => n.id === parseInt(params.data.id))
            if (!node) return ''
            return `
              <div>
                <strong>${node.name}</strong><br/>
                编码: ${node.code}<br/>
                类型: ${node.type || '未知'}<br/>
                级别: ${node.data_level}
              </div>
            `
          }
          return ''
        }
      },
      legend: {
        data: Object.keys(levelColors).map(level => ({
          name: level,
          icon: 'circle',
          itemStyle: { color: levelColors[level] }
        })),
        orient: 'vertical',
        left: 'left',
        top: 'middle'
      },
      series: [
        {
          type: 'graph',
          layout: 'force',
          data: graphNodes,
          links: graphLinks,
          roam: true,
          label: {
            show: true,
            position: 'right',
            formatter: '{b}'
          },
          labelLayout: {
            hideOverlap: true
          },
          lineStyle: {
            color: 'source',
            curveness: 0.3
          },
          emphasis: {
            focus: 'adjacency',
            lineStyle: {
              width: 4
            }
          },
          force: {
            repulsion: 1000,
            gravity: 0.1,
            edgeLength: 200,
            layoutAnimation: true
          },
          categories: Object.keys(levelColors).map(level => ({
            name: level,
            itemStyle: { color: levelColors[level] }
          }))
        }
      ]
    }

    chart.setOption(option)

    // 响应式调整
    const handleResize = () => {
      chart.resize()
    }
    window.addEventListener('resize', handleResize)

    return () => {
      window.removeEventListener('resize', handleResize)
      if (chartInstance.current) {
        chartInstance.current.dispose()
        chartInstance.current = null
      }
    }
  }, [nodes, edges, centerNodeId])

  return (
    <div
      ref={chartRef}
      style={{
        width: '100%',
        height: `${height}px`,
        minHeight: '400px'
      }}
    />
  )
}

export default LineageGraph

