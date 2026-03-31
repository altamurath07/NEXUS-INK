# NEXUS-INK

As a JJK fan, keeping up with the internet is a full-time job, with the finishing of JJK Season 3 my mornings on the  r/JuJutsuKaisen front page is forty threads deep in anime fans asking "wait does Gojo win the fight with Sukuna" — spoiler he doesn't, he gets cut in half by mahoraga, and the manga community has known this for two years and it's exhausting; some insisting Megumi will be freed from Sukuna by the power of friendship, and one unhinged posts arguing that Kenjaku's  been controlling Gege Akutami's hand since chapter 1 to deliberately cause reader suffering as a cursed technique. Filtering through all of that with two thumbs and a phone screen is, frankly, a war of attention-span I was losing.

Which inspired me to make NEXUS-INK, a standalone e-ink news terminal built around the Orange Pi 5 Plus: it pulls posts from whatever subreddits the user specifies (see Python files), summarises them locally using a small on-device LLM, and displays the result on a 7.5-inch e-ink screen — no notifications, no algorithm, no glare, no doom-scrolling. Just the good stuff, distilled, on a screen that looks and feels like paper.

---
## Wiring Diagram (using mermaid)
```mermaid
flowchart TD
    PWR["5V Power Input\n5V 4A or higher"]
    OPI["Orange Pi 5 Plus\nRK3588 / 32GB LPDDR4X\n6 TOPS NPU"]

    PWR -->|5V main power| OPI
    PWR -.-|Shared GND| OPI

    subgraph DISPLAY [Display Chain]
        EINK["Waveshare 7.8-inch E-Ink HAT\nIT8951 built-in\n1872x1404"]
        FOAM["Foam Baffle 0.4mm"]
        FOAM -->|seal airflow gap| EINK
    end

    subgraph INPUT [Input]
        ENC[EC11 Rotary Encoder]
    end

    subgraph THERMAL [Thermal]
        FAN[5V Blower Fan]
        HS[40x40mm Heatsink]
        VENT[Side Vent]
        HS -->|heat transfer to fan| FAN
        FAN -->|side exhaust| VENT
    end

    subgraph STORAGE [Storage]
        SSD[128GB NVMe SSD]
    end

    PWR -->|5V display board| EINK
    OPI -->|SPI or USB data| EINK
    OPI -->|PCIe 3.0 x4 M.2| SSD
    OPI -->|GPIO A/B/SW 3.3V GND| ENC
    OPI -->|5V fan header| FAN
    OPI -->|SoC heat| HS
```

---
## Full Assembly Render
<div style="display:flex;flex-wrap:wrap;gap:8px;justify-content:center;">
  <div style="display:flex;gap:8px;width:100%;justify-content:center;">
    <img width="248" height="127" alt="image" src="https://github.com/user-attachments/assets/478c9c78-7ace-4763-b7dc-9d4161e2054e" />
    <img width="247" height="125" alt="image" src="https://github.com/user-attachments/assets/cf6f8480-4a40-4476-83f0-f8a52f8c5ecf" />
    <img width="248" height="128" alt="image" src="https://github.com/user-attachments/assets/6c351331-ac4b-4aee-bb31-0cb07515e34f" />
  </div>
  <div style="display:flex;gap:8px;width:100%;justify-content:center;">
    <img width="248" height="127" alt="image" src="https://github.com/user-attachments/assets/798fcd37-b054-4778-b4e6-989a2308046f" />
    <img width="247" height="126" alt="image" src="https://github.com/user-attachments/assets/9b993326-2336-472e-8b6b-2ac8d00bba1d" />
  </div>
</div>

## Rough Hardware Render

<div style="display:flex;flex-wrap:wrap;gap:8px;justify-content:center;">
  <div style="display:flex;gap:8px;width:100%;justify-content:center;">
    <img width="248" height="124" alt="image" src="https://github.com/user-attachments/assets/ad3b5d61-ec14-450e-a4c3-c46bf33c7733" />
    <img width="248" height="127" alt="image" src="https://github.com/user-attachments/assets/237ba2f7-a345-4414-b9f1-c01eedd1374f" />
    <img width="247" height="124" alt="image" src="https://github.com/user-attachments/assets/6f0713c5-afb9-4974-b731-a1db93be9f11" />
  </div>
  <div style="display:flex;gap:8px;width:100%;justify-content:center;">
    <img width="248" height="125" alt="image" src="https://github.com/user-attachments/assets/decefa9c-fc30-4942-90dd-5b8712111e8b" />
    <img width="248" height="128" alt="image" src="https://github.com/user-attachments/assets/5d5441de-5200-49e9-a5e1-9e4727e7e906" />
  </div>
</div>

## Bill of Materials (BOM)
| Comment | Location | Interface | Link | Quantity | Total Price |
|---|---|---|---|---|---|
| **Orange Pi 5 Plus 32GB** | **Base mount, centre** | **—** | **https://www.alibaba.com/product-detail/Orange-Pi-5-Plus-32GB-RAM_1601051236285.html** | **1** | **€230.00** |
| **Waveshare 7.8inch E-Ink HAT** | **Front face, top panel** | **SPI / USB** | **https://www.alibaba.com/product-detail/WaveShare-1872-X-1404-7-8Inch_1600763875848.html** | **1** | **€115.00** |
| EC11 Rotary Encoder | Right side panel | GPIO BCM 17/18/27 | https://www.aliexpress.com | 1 | ~€2.00 |
| 128GB NVMe SSD M.2 2280 | OPi M.2 slot | PCIe 3.0 x4 | https://www.amazon.it | 1 | ~€20.00 |
| 5V Blower Fan 50×15mm | Rear internal | 5V fan header | https://www.aliexpress.com | 1 | ~€5.00 |
| 40×40mm Aluminium Heatsink | OPi SoC top | Thermal adhesive | https://www.aliexpress.com | 1 | ~€4.00 |
| 5V 4A Power Supply USB-C | Rear port | 5V rail | https://www.amazon.it | 1 | ~€10.00 |
| Foam Baffle Strip 0.4mm | Display perimeter | Adhesive | https://www.aliexpress.com | 1 | ~€2.00 |
| Dupont Jumper Wires F-F 10cm | Internal routing | GPIO headers | https://www.aliexpress.com | 1 set | ~€2.00 |
| 3D Printed Shell | Outer enclosure | — | — | 1 | Free |

> **Bold items are funded by Hackclub**
>
> **Total requested from Hackclub: €345 (€230.00 + €115.00), est ≈398 usd **
> 
> Self-funded estimate: ~€45, est ≈52 usd














