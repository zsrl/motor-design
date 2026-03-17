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
2. **常见项目文件夹**：创建一个新的文件夹，命名为“motor-时间戳”（例如：motor-20240610123000），后续文件参数文件保存到这个文件夹下。
3. **生成并保存参数**：创建合适的RMxprt JSON参数字符串，生成的json数据要严格参考下面的JSON Schema定义，以及其中的描述。使用你write_file的工具，将参数保存到动态命名的JSON文件（rmxprt_params.json）。并且将生成的参数要以文字形式输出到界面，方便用户查看/
4. **执行脚本**：然后调用 `{
  "command": "python \"E:\\Code\\kshc\\rmxprt_design.py\" \"{filename}\""
}` 运行RMxprt设计，执行此脚本时，timeout设置为1200秒（20分钟），以确保有足够的时间完成仿真。

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
          "description": "定子内径，是外径的70%",
          "pattern": "^\\d+(\\.\\d+)?mm$",
          "examples": ["40mm", "80mm", "150mm", "250mm"]
        },
        "Length": {
          "type": "string",
          "description": "定子长度",
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
          "description": "槽身高度2，定子直径的10%",
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
          "description": "每槽导体数，固定为0",
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
          "description": "转子外径, D(定子外径)减2mm",
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
          "description": "转子长度",
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
          "default": "NAlliance - N35UH"
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
    }
  }
}
```