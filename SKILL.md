---
name: motor-design
description: 指导AI如何生成RMxprt电机设计参数的JSON字符串，并自动调用命令行运行RMxprt设计脚本。解释每个参数的意义、取值范围、单位，以及完整的JSON数据结构。当用户需要创建或修改RMxprt电机设计参数并立即运行仿真时使用此技能。
---

# 电机设计技能

本技能指导AI如何生成RMxprt电机设计参数的JSON字符串，并自动调用命令行运行Ansys AEDT RMxprt设计脚本。这是一个完整的端到端解决方案，专门针对RMxprt电机设计工具。

# 常见类型电机参考

风扇电机: 12槽8极
水泵电机: 9槽6极
伺服电机: 24槽8极

## 完整工作流程

1. **分析需求**：理解用户需要的电机规格和类型
2. **生成参数**：创建合适的RMxprt JSON参数字符串，生成的json数据要严格参考下面的JSON Schema定义，以及其中的描述。
3. **保存参数**：生成当前时间戳timestamp，格式YYYYMMDDHHMMSS（记住这个时间戳，后续流程需要用到），将参数保存到动态命名的JSON文件（rmxprt_params_{timestamp}.json），此步骤不需要将结果输出到界面，等执行完脚本再以表格形式展示参数。
4. **执行脚本**：然后调用该技能scripts下的rmxprt_design.py脚本，传入timestamp参数，命令格式如下： `{
  "command": "python \"{path}\\scripts\\rmxprt_design.py\" \"{timestamp}\""
}` path是该技能的文件夹位置，运行RMxprt设计，执行此脚本时，timeout设置为1200秒（20分钟），以确保有足够的时间完成仿真。
5. **参数展示**：将生成的参数要以表格形式输出到界面，方便用户查看。
6. **结果分析**：仿真完成后，请求用户将仿真结果的solution_data内容提供给AI（注意由用户对话提供，不要再工作区寻找），若用户提供，根据本文档内的结果分析规则，分析仿真结果。如果用户发来的solution_data符合要求，则工作结束；如果不符合要求，则并重新执行工作流程，优化参数。

## RMxprt参数详细说明 及 JSON Schema定义

以下是RMxprt电机参数的JSON Schema定义，用于验证参数JSON的结构和数据类型：

```json
{
  "title": "RMxprt电机设计参数",
  "description": "Ansys AEDT RMxprt电机设计参数的JSON Schema定义",
  "type": "object",
  "properties": {
    "General": {
      "type": "object",
      "description": "通用电机参数",
      "properties": {
        "Number of Poles": {
          "type": "integer",
          "description": "电机极数",
          "minimum": 2,
          "maximum": 24,
          "examples": [2, 4, 6, 8, 10, 12]
        },
        "Rotor Position": {
          "type": "string",
          "description": "转子类型",
          "enum": ["Inner Rotor", "Outer Rotor"],
          "default": "Inner Rotor"
        },
        "Frictional Loss": {
          "type": "string",
          "description": "摩擦损耗，默认为0",
          "pattern": "^\\d+(\\.\\d+)?W$",
          "default": "0W",
          "examples": ["0W", "10W", "50W"]
        },
        "Windage Loss": {
          "type": "string",
          "description": "风磨损耗，默认为0",
          "pattern": "^\\d+(\\.\\d+)?W$",
          "default": "0W",
          "examples": ["0W", "5W", "20W"]
        },
        "Reference Speed": {
          "type": "string",
          "description": "参考转速，必须大于额定转速300转",
          "pattern": "^\\d+(\\.\\d+)?rpm$",
          "examples": ["1000rpm", "3000rpm", "6000rpm"]
        },
        "Control Type": {
          "type": "string",
          "description": "控制类型",
          "enum": ["DC", "AC"],
          "default": "DC"
        },
        "Circuit Type": {
          "type": "string",
          "description": "电路类型，固定Y3",
          "enum": ["Y3"],
          "default": "Y3"
        }
      }
    },
    "Stator": {
      "type": "object",
      "description": "定子参数",
      "properties": {
        "Outer Diameter": {
          "type": "string",
          "description": "定子外径, 根据用户需求的体积大小来确定",
          "pattern": "^\\d+(\\.\\d+)?mm$",
          "examples": ["50mm", "100mm", "200mm", "300mm"]
        },
        "Inner Diameter": {
          "type": "string",
          "description": "定子内径，初始设置为外径的70%，后续可以根据槽尺寸要求调整",
          "pattern": "^\\d+(\\.\\d+)?mm$",
          "examples": ["40mm", "80mm", "150mm", "250mm"]
        },
        "Length": {
          "type": "string",
          "description": "定子高度",
          "pattern": "^\\d+(\\.\\d+)?mm$",
          "examples": ["50mm", "100mm", "200mm", "300mm"]
        },
        "Stacking Factor": {
          "type": "number",
          "description": "叠压系数，固定0.975",
          "minimum": 0.90,
          "maximum": 0.98,
          "default": 0.95
        },
        "Steel Type/Material": {
          "type": "string",
          "description": "钢材类型，固定为DW310_35",
          "default": "DW310_35"
        },
        "Number of Slots": {
          "type": "integer",
          "description": "槽数",
        },
        "Slot Type/SlotType": {
          "type": "number",
          "description": "槽型，固定为3",
          "default": 3
        },
        "Skew Width": {
          "type": "number",
          "description": "斜槽宽度，固定为0",
          "minimum": 0,
          "maximum": 10,
          "default": 0
        }
      }
    },
    "Slot": {
      "type": "object",
      "description": "槽参数",
      "properties": {
        "Auto Design": {
          "type": "boolean",
          "description": "自动设计，固定为false",
          "default": false
        },
        "Hs0": {
          "type": "string",
          "description": "槽口高度，固定为1mm",
          "pattern": "^\\d+(\\.\\d+)?mm$",
          "default": "0mm",
          "examples": ["0.5mm", "1mm", "2mm"]
        },
        "Hs1": {
          "type": "string",
          "description": "槽身高度1， 固定为1mm",
          "pattern": "^\\d+(\\.\\d+)?mm$",
          "default": "0mm"
        },
        "Hs2": {
          "type": "string",
          "description": "槽身高度2，初始为定子直径的10%，后续可以根据槽尺寸要求动态调整",
          "pattern": "^\\d+(\\.\\d+)?mm$",
          "default": "0mm"
        },
        "Bs0": {
          "type": "string",
          "description": "槽口宽度, 固定为2mm",
          "pattern": "^\\d+(\\.\\d+)?mm$",
          "default": "0mm",
          "examples": ["1mm", "2mm", "3mm"]
        },
        
        "Bs1": {
          "type": "string",
          "description": "槽身宽度1,如果是12槽的，定子外径周长的1/24",
          "pattern": "^\\d+(\\.\\d+)?mm$",
          "default": "0mm"
        },
        
        "Bs2": {
          "type": "string",
          "description": "槽身宽度2， Bs1的1.3倍",
          "pattern": "^\\d+(\\.\\d+)?mm$",
          "default": "0mm"
        },
        "Rs": {
          "type": "string",
          "description": "槽底半径， 固定为0",
          "pattern": "^\\d+(\\.\\d+)?mm$",
          "default": "0mm"
        }
      }
    },
    "Winding": {
      "type": "object",
      "description": "绕组参数",
      "properties": {
        "Winding Layers": {
          "type": "integer",
          "description": "绕组层数， 固定为2",
          "minimum": 1,
          "maximum": 2,
          "default": 2
        },
        "Winding Type": {
          "type": "string",
          "description": "绕组类型，固定为Whole-Coiled",
          "enum": ["Whole-Coiled", "Half-Coiled"],
          "default": "Whole-Coiled"
        },
        "Parallel Branches": {
          "type": "integer",
          "description": "并联支路数，固定为1",
          "minimum": 1,
          "default": 1
        },
        "Conductors per Slot": {
          "type": "integer",
          "description": "绕线圈数，默认为0，后续要根据分析结果调整",
          "minimum": 1,
          "default": 0
        },
        "Coil Pitch": {
          "type": "integer",
          "description": "线圈节距，固定为1"
          "default": 1
        },
        "Number of Strands": {
          "type": "integer",
          "description": "股数，固定为0",
          "minimum": 1,
          "default": 1
        },
        "Wire Wrap": {
          "type": "string",
          "description": "线包厚度， 固定为0.05",
          "pattern": "^\\d+(\\.\\d+)?mm$",
          "default": "0mm",
          "examples": ["0.1mm", "0.2mm"]
        },
       "Wire Size/WireSizeWireDiameter": {
          "type": "string",
          "description": "固定为0",
          "default": "0mm",
        },
        "Wire Size/WireSizeGauge": {
          "type": "string",
          "description": "固定为AUTO",
          "default": "AUTO"
        },
        "Input Half-turn Length": {
          "type": "boolean",
          "description": "输入半匝长度，固定为false",
          "default": false
        },
        "End Extension": {
          "type": "number",
          "description": "端部延伸长度, 固定为0",
          "pattern": "^\\d+(\\.\\d+)?mm$",
          "default": 0
        },
        "Base Inner Radius": {
          "type": "number",
          "description": "基圆内半径, 固定为0",
          "pattern": "^\\d+(\\.\\d+)?mm$",
          "default": 0
        },
        "Tip Inner Diameter": {
          "type": "number",
          "description": "尖端内径, 固定为0",
          "pattern": "^\\d+(\\.\\d+)?mm$",
          "default": 0
        },
        "End Clearance": {
          "type": "number",
          "description": "端部间隙, 固定为0",
          "pattern": "^\\d+(\\.\\d+)?mm$",
          "default": 0
        },
        "Slot Liner": {
          "type": "number",
          "description": "槽衬厚度, 固定为0.3",
          "pattern": "^\\d+(\\.\\d+)?mm$",
          "default": 0.3
        },
        "Wedge Thickness": {
          "type": "number",
          "description": "楔形厚度, 固定为0",
          "pattern": "^\\d+(\\.\\d+)?mm$",
          "default": 0
        },
        "Layer Insulation": {
          "type": "number",
          "description": "层间绝缘厚度",
          "pattern": "^\\d+(\\.\\d+)?mm$",
          "default": 0
        },
        "Limited Fill Factor": {
          "type": "number",
          "description": "有限填充系数, 固定为0.75",
          "default": 0.75
        }
      }
    },
    "Rotor": {
      "type": "object",
      "description": "转子参数",
      "properties": {
        "Outer Diameter": {
          "type": "string",
          "description": "转子外径, D(定子内径)减2mm",
          "pattern": "^\\d+(\\.\\d+)?mm$",
          "examples": ["39mm", "79mm", "149mm", "249mm"]
        },
        "Inner Diameter": {
          "type": "string",
          "description": "转子内径，大概是转子外径25%",
          "pattern": "^\\d+(\\.\\d+)?mm$",
          "examples": ["15mm", "30mm", "50mm", "100mm"]
        },
        "Length": {
          "type": "string",
          "description": "转子高度，需与定子高度一致",
          "pattern": "^\\d+(\\.\\d+)?mm$",
          "examples": ["50mm", "100mm", "200mm", "300mm"]
        },
        "Steel Type/Material": {
          "type": "string",
          "description": "钢材类型，转子和定子的材料是一致的",
          "default": "DW310_35"
        },
        "Stacking Factor": {
          "type": "number",
          "description": "叠压系数，固定0.975",
          "minimum": 0.90,
          "maximum": 0.98,
          "default": 0.975
        },
        "Pole Type/PoleType": {
          "type": "integer",
          "description": "磁极类型，固定为1",
          "minimum": 1,
          "maximum": 10,
          "default": 1
        }
      }
    },
    "Pole": {
      "type": "object",
      "description": "磁极参数",
      "properties": {
        "Embrace": {
          "type": "number",
          "description": "级弧系数，固定0.7",
          "default": 0.7
        },
        "Offset": {
          "type": "string",
          "description": "偏移量，固定为0mm",
          "pattern": "^\\d+(\\.\\d+)?mm$",
          "default": "0mm",
          "examples": ["0mm", "1mm", "2mm"]
        },
        "Magnet Type/Material": {
          "type": "string",
          "description": "磁钢类型, 固定Alliance - N35UH",
          "default": "Alliance - N35UH"
        },
        "Magnet Thickness": {
          "type": "string",
          "description": "磁钢厚度，默认2.5",
          "pattern": "^\\d+(\\.\\d+)?mm$",
          "default": "0mm"
        }
      }
    },
    "Shaft": {
      "type": "object",
      "description": "轴参数",
      "properties": {
        "Magnetic Shaft": {
          "type": "boolean",
          "description": "磁性轴，固定false",
          "default": false
        }
      }
    },
    "Circuit": {
      "type": "object",
      "description": "电路参数, Control Type为DC的时候，才需要设置",
      "properties": {
        "Trigger Pulse Width": {
          "type": "string",
          "description": "触发脉冲宽度，默认120deg",
          "pattern": "^\\d+(\\.\\d+)?deg$",
          "default": "120deg",
        },
        "Transistor Drop": {
          "type": "string",
          "description": "晶体管压降，固定为0.2V",
          "pattern": "^\\d+(\\.\\d+)?V$",
          "default": "0.2V"
        },
        "Diode Drop": {
          "type": "string",
          "description": "二极管压降， 固定为0.2V",
          "pattern": "^\\d+(\\.\\d+)?V$",
          "default": "0.2V"
        }
      }
    },
    "Setup": {
      "type": "object",
      "description": "用于求解分析的设置参数",
      "properties": {
        "Enabled": {
          "type": "boolean",
          "description": "是否启用分析设置，固定为true",
          "default": true
        },
        "LoadType": {
          "type": "string",
          "description": "负载类型，固定为ConstPower",
          "default": "ConstPower"
        },
        "OperatingTemperature": {
          "type": "string",
          "description": "工作温度，默认为55cel，可以根据用户需求修改",
          "pattern": "^\\d+(\\.\\d+)?cel$",
          "default": "55cel",
        },
        "OperationType": {
          "type": "string",
          "description": "操作类型，固定为Motor",
          "default": "Motor"
        },
        "RatedOutputPower": {
          "type": "string",
          "description": "额定输出功率，根据用户的需求设定",
          "pattern": "^\\d+(\\.\\d+)?kW$",
          "default": "1kW"
        },
        "RatedSpeed": {
          "type": "string",
          "description": "额定转速，根据用户的需求设定",
          "pattern": "^\\d+(\\.\\d+)?rpm$",
          "default": "1000rpm"
        },
        "RatedVoltage": {
          "type": "string",
          "description": "额定电压，根据用户的需求设定",
          "pattern": "^\\d+(\\.\\d+)?V$",
          "default": "100V"
        }
      }
    }
  }
}
```

## 结果分析规则

1、Limited Slot Fill Factor (%)（槽满率）需要在65到75之间， 如果槽满率过高，应该调整槽尺寸等参数，使其满足槽满率曹满率小于75%。

2、Minimum Air Gap (mm)（最小气隙）对电机性能有重要影响。如果仿真结果显示齿槽转矩过大，说明磁路不够平滑，此时需要缩小最小气隙的值；反之，如果齿槽转矩过小，则可以适当放大最小气隙的值。调整最小气隙实际上就是调整定子内径和转子外径之间的差值。

3、Stator-Teeth Flux Density (Tesla)（定子齿磁密）如果仿真结果显示定子齿磁密过高，可能导致铁损增加和过热问题，此时需要调整定子材料、槽型或增加槽数等参数来降低磁密；反之，如果定子齿磁密过低，则可以适当减少槽数或调整槽型来提高磁密。我们要求此参数需小于1.6。

4、Stator-Yoke Flux Density (Tesla)（定子轭磁密）如果仿真结果显示定子轭磁密过高，可能导致铁损增加和过热问题，此时需要调整定子材料、增加定子厚度或优化槽型等参数来降低磁密；反之，如果定子轭磁密过低，则可以适当减少定子厚度或调整槽型来提高磁密。我们要求此参数需小于1.6。如果此值过高，需要通过缩小槽型的H2

5、Rotor-Yoke Flux Density (Tesla)（转子轭磁密）如果仿真结果显示转子轭磁密过高，可能导致铁损增加和过热问题，此时需要调整转子材料、增加转子厚度或优化极型等参数来降低磁密；反之，如果转子轭磁密过低，则可以适当减少转子厚度或调整极型来提高磁密。我们要求此参数需小于1.8。

6、Cogging Torque (N.m)（齿槽转矩）如果仿真结果显示齿槽转矩过大，可能导致电机运行不平稳和噪音增加，此时需要调整最小气隙、槽型或增加斜槽等参数来降低齿槽转矩；反之，如果齿槽转矩过小，则可以适当放大最小气隙或调整槽型来提高齿槽转矩。我们要求此参数不超过额定转矩的5%。

7、Maximum Line Induced Voltage (V)（反电动势）跟输入电压对比，需要低于额定电压，调整气息，气隙越大，反电动势越小。

8、Armature Thermal Load (A^2/mm^3)（电枢热负荷）需要小于750以内比较安全，如果仿真结果显示电枢热负荷过高，可能导致绕组过热和绝缘损坏，此时需要调整每槽导体数、线径或增加散热措施等参数来降低热负荷；反之，如果电枢热负荷过低，则可以适当增加每槽导体数或线径来提高热负荷。

9、Armature Current Density (A/mm^2)（电枢电流密度）需要小于7，比较安全，如果仿真结果显示电枢电流密度过高，可能导致绕组过热和绝缘损坏，此时需要调整每槽导体数、线径或增加散热措施等参数来降低电流密度；反之，如果电枢电流密度过低，则可以适当增加每槽导体数或线径来提高电流密度。

10、No-Load Input Power (W)（空载输入功率），合理值在额定功率的2%到5%之间，如果空载输入功率过大，应该增加绕线圈数。

10、Efficiency (%)（效率）需要大于90%，如果仿真结果显示效率过低，可能说明电机设计存在较大的损耗问题，此时需要分析损耗来源（如铁损、铜损、机械损等），并调整相关参数（如材料选择、槽型设计、绕组配置等）来提高效率；这是评估一个电机设计优劣的关键指标，效率过低可能导致电机性能不佳和能耗增加。

11、Rated Torque (N.m) 这是额定转矩，需要参考。

12、Torque Angle (degree)（功角）它的绝对值需要在25-40度之间，如果仿真结果显示功角绝对值过大，可能导致电机运行不稳定和振动增加，此时需要调整磁极类型、槽型或增加斜槽等参数来降低功角绝对值；反之，如果功角绝对值过小，则可以适当调整磁极类型或槽型来提高功角绝对值。如果功角绝对值较小，通过减定子和转子的高度、增加绕线圈数，来调节，反之亦然。

**目标**：

第一步：调正确槽满率
第二步：调正确功角
第三步：调正确其他参数