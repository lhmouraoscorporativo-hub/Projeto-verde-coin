#!/usr/bin/env python3
"""
Gerador de Mapas de Calor - Zonas Quentes de Emissões de Carbono
VerdeCoin - Sistema de Compensação de Carbono
Versão 1.0 - Testável localmente
"""

import json
import math
from datetime import datetime

class EmissionHeatMapGenerator:
    """Gerador de mapas de calor para visualizar zonas quentes de emissões."""
    
    def __init__(self):
        self.emission_data = []
        self.html_content = ""
    
    def add_emission_sources(self, sources):
        """Adiciona fontes de emissão."""
        self.emission_data.extend(sources)
        print(f"✅ {len(sources)} fontes adicionadas. Total: {len(self.emission_data)}")
    
    def generate_html_map(self, output_file='emissions_map.html'):
        """Gera arquivo HTML com mapa de calor interativo."""
        
        if not self.emission_data:
            print("❌ Erro: Nenhuma fonte de emissão disponível!")
            return None
        
        # Preparar dados para Leaflet.heat
        heat_data = []
        markers_data = []
        
        for source in self.emission_data:
            # Formato para heatmap: [lat, lng, intensity]
            heat_data.append({
                'lat': source['latitude'],
                'lng': source['longitude'],
                'intensity': source['intensity']
            })
            
            # Preparar marcadores
            markers_data.append({
                'lat': source['latitude'],
                'lng': source['longitude'],
                'name': source['name'],
                'type': source['type'],
                'emission': source['emission_tons_co2'],
                'intensity': source['intensity']
            })
        
        # Calcular estatísticas
        total_emission = sum(s['emission_tons_co2'] for s in self.emission_data)
        avg_emission = total_emission / len(self.emission_data)
        
        print(f"\n📊 Estatísticas:")
        print(f"   Total de emissão: {total_emission:,.0f} ton CO₂")
        print(f"   Média por fonte: {avg_emission:,.0f} ton CO₂")
        print(f"   Número de focos: {len(self.emission_data)}")
        
        # Criar HTML
        html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🌍 VerdeCoin - Mapa de Emissões do PID</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css" />
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" />
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            height: 100vh;
            overflow: hidden;
        }}
        
        .container {{
            display: flex;
            height: 100vh;
            gap: 0;
        }}
        
        .sidebar {{
            width: 400px;
            background: white;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
            overflow-y: auto;
            padding: 25px;
            z-index: 100;
        }}
        
        .sidebar h1 {{
            color: #2c3e50;
            margin-bottom: 5px;
            font-size: 28px;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .sidebar p {{
            color: #7f8c8d;
            font-size: 13px;
            margin-bottom: 25px;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
            margin-bottom: 25px;
        }}
        
        .stat-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 18px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        
        .stat-card h3 {{
            font-size: 12px;
            opacity: 0.9;
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .stat-card .value {{
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 4px;
        }}
        
        .stat-card small {{
            font-size: 11px;
            opacity: 0.8;
        }}
        
        .legend {{
            background: #f8f9fa;
            padding: 18px;
            border-radius: 10px;
            margin-bottom: 25px;
            border-left: 4px solid #667eea;
        }}
        
        .legend h3 {{
            color: #2c3e50;
            font-size: 14px;
            margin-bottom: 15px;
            font-weight: 600;
        }}
        
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 10px;
            font-size: 13px;
            color: #555;
        }}
        
        .legend-color {{
            width: 24px;
            height: 24px;
            border-radius: 4px;
            flex-shrink: 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        .legend-item:last-child {{
            margin-bottom: 0;
        }}
        
        .top-emitters {{
            background: #f8f9fa;
            padding: 18px;
            border-radius: 10px;
            border-left: 4px solid #e74c3c;
        }}
        
        .top-emitters h3 {{
            color: #2c3e50;
            font-size: 14px;
            margin-bottom: 15px;
            font-weight: 600;
        }}
        
        .emitter-item {{
            padding: 12px;
            background: white;
            margin-bottom: 10px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
            cursor: pointer;
            transition: all 0.3s ease;
            font-size: 13px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }}
        
        .emitter-item:hover {{
            transform: translateX(5px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            background: #f0f4ff;
        }}
        
        .emitter-item .name {{
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 4px;
        }}
        
        .emitter-item .type {{
            color: #7f8c8d;
            font-size: 12px;
            margin-bottom: 4px;
        }}
        
        .emitter-item .value {{
            color: #e74c3c;
            font-weight: bold;
        }}
        
        #map {{
            flex: 1;
            position: relative;
        }}
        
        .map-header {{
            position: absolute;
            top: 20px;
            left: 420px;
            background: white;
            padding: 18px 24px;
            border-radius: 10px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            z-index: 10;
            max-width: 320px;
        }}
        
        .map-header h2 {{
            color: #2c3e50;
            font-size: 18px;
            margin-bottom: 6px;
            font-weight: 600;
        }}
        
        .map-header p {{
            color: #7f8c8d;
            font-size: 13px;
        }}
        
        .timestamp {{
            position: absolute;
            bottom: 20px;
            left: 420px;
            background: white;
            padding: 12px 16px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            font-size: 12px;
            color: #7f8c8d;
            z-index: 10;
        }}
        
        ::-webkit-scrollbar {{
            width: 8px;
        }}
        ::-webkit-scrollbar-track {{
            background: #f1f1f1;
        }}
        ::-webkit-scrollbar-thumb {{
            background: #667eea;
            border-radius: 4px;
        }}
        
        @media (max-width: 1024px) {{
            .container {{
                flex-direction: column;
            }}
            .sidebar {{
                width: 100%;
                max-height: 35vh;
            }}
            #map {{
                height: 65vh;
            }}
            .map-header {{
                left: 20px;
            }}
            .timestamp {{
                left: 20px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="sidebar">
            <h1>🌱 VerdeCoin</h1>
            <p>🗺️ Mapa de Zonas Quentes - Emissões de Carbono do PID</p>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <h3>Emissão Total</h3>
                    <div class="value">{total_emission:,.0f}</div>
                    <small>ton CO₂</small>
                </div>
                <div class="stat-card">
                    <h3>Fontes Ativas</h3>
                    <div class="value">{len(self.emission_data)}</div>
                    <small>focos</small>
                </div>
            </div>
            
            <div class="legend">
                <h3>🌡️ Escala de Intensidade</h3>
                <div class="legend-item">
                    <div class="legend-color" style="background: linear-gradient(135deg, #28a745, #20c997);"></div>
                    <span><strong>Baixa:</strong> 0-30%</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="background: linear-gradient(135deg, #ffc107, #ffb300);"></div>
                    <span><strong>Média:</strong> 30-60%</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="background: linear-gradient(135deg, #fd7e14, #ff6c00);"></div>
                    <span><strong>Alta:</strong> 60-80%</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="background: linear-gradient(135deg, #dc3545, #c82333);"></div>
                    <span><strong>Crítica:</strong> 80-100%</span>
                </div>
            </div>
            
            <div class="top-emitters">
                <h3>🏆 Top 5 Maiores Emissores</h3>
                <div id="topEmittersList"></div>
            </div>
        </div>
        
        <div id="map"></div>
        <div class="map-header">
            <h2>🗺️ Mapa do PID</h2>
            <p>💡 Clique nos marcadores para detalhes completos</p>
        </div>
        <div class="timestamp">
            ⏰ Atualizado: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
        </div>
    </div>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet-heat/0.2.0/leaflet-heat.min.js"></script>
    
    <script>
        // Dados de emissões
        const emissionData = {json.dumps(markers_data)};
        
        console.log('✅ Dados carregados:', emissionData.length, 'fontes');
        
        // Inicializar mapa
        const map = L.map('map').setView([-14.2350, -51.9253], 4);
        L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
            attribution: '© OpenStreetMap',
            maxZoom: 19
        }}).addTo(map);
        
        // Heat layer data
        const heatData = emissionData.map(d => [d.lat, d.lng, d.intensity]);
        L.heatLayer(heatData, {{ 
            radius: 50, 
            blur: 30, 
            maxZoom: 13,
            gradient: {{0.2: 'green', 0.4: 'yellow', 0.6: 'orange', 0.8: 'red', 1.0: 'darkred'}}
        }}).addTo(map);
        
        // Função para determinar cor
        function getColor(intensity) {{
            if (intensity > 0.8) return '#dc3545';
            if (intensity > 0.6) return '#fd7e14';
            if (intensity > 0.3) return '#ffc107';
            return '#28a745';
        }}
        
        // Adicionar marcadores
        emissionData.forEach(data => {{
            const marker = L.circleMarker([data.lat, data.lng], {{
                radius: 8 + (data.intensity * 8),
                fillColor: getColor(data.intensity),
                color: '#fff',
                weight: 3,
                opacity: 1,
                fillOpacity: 0.8
            }}).bindPopup(`
                <div style="font-size: 13px; font-weight: 500;">
                    <b style="font-size: 14px; color: #2c3e50;">📍 ${{data.name}}</b><br><hr style="margin: 6px 0;">
                    <span style="color: #667eea;"><strong>Tipo:</strong></span> ${{data.type}}<br>
                    <span style="color: #e74c3c;"><strong>Emissão:</strong></span> <strong>${{data.emission.toLocaleString('pt-BR')}} ton CO₂</strong><br>
                    <span style="color: #667eea;"><strong>Intensidade:</strong></span> ${{(data.intensity * 100).toFixed(1)}}%<br>
                    <span style="font-size: 11px; color: #7f8c8d;">📡 Lat: ${{data.lat.toFixed(4)}}, Lng: ${{data.lng.toFixed(4)}}</span>
                </div>
            `, {{ maxWidth: 300 }});
            marker.addTo(map);
        }});
        
        // Top emitters
        const topEmitters = emissionData.sort((a, b) => b.emission - a.emission).slice(0, 5);
        const topList = document.getElementById('topEmittersList');
        topEmitters.forEach((emitter, idx) => {{
            const div = document.createElement('div');
            div.className = 'emitter-item';
            div.innerHTML = `
                <div style="display: flex; justify-content: space-between; align-items: start;">
                    <div>
                        <div class="name">{{idx + 1}}. ${{emitter.name}}</div>
                        <div class="type">${{emitter.type.replace(/_/g, ' ')}}</div>
                    </div>
                    <div style="text-align: right;">
                        <div class="value">${{emitter.emission.toLocaleString('pt-BR')}}</div>
                        <div style="font-size: 11px; color: #7f8c8d;">ton CO₂</div>
                    </div>
                </div>
            `;
            topList.appendChild(div);
        }});
        
        console.log('✅ Mapa renderizado com sucesso!');
    </script>
</body>
</html>
"""
        
        # Salvar arquivo
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"\n✨ Arquivo gerado: {output_file}")
        print(f"📖 Abra no navegador: file:///{__file__.replace('emissions_heatmap.py', output_file)}")
        
        return output_file


# ============= TESTE AGORA =============

if __name__ == "__main__":
    print("🚀 Iniciando gerador de mapa de emissões...\n")
    
    # Criar gerador
    generator = EmissionHeatMapGenerator()
    
    # Dados de exemplo: principais zonas quentes de emissão no Brasil
    emission_sources = [
        # São Paulo - Polo Industrial
        {'latitude': -23.5505, 'longitude': -46.6333, 'intensity': 0.95, 
         'type': 'factory', 'name': 'Polo Industrial São Paulo', 'emission_tons_co2': 15000},
        
        # Rio de Janeiro - Refino e Portuário
        {'latitude': -22.9068, 'longitude': -43.1729, 'intensity': 0.88,
         'type': 'refinery', 'name': 'Complexo Petroquímico Rio', 'emission_tons_co2': 12000},
        
        # Minas Gerais - Siderurgia
        {'latitude': -19.9191, 'longitude': -43.9386, 'intensity': 0.92,
         'type': 'steel_factory', 'name': 'Siderúrgica MG', 'emission_tons_co2': 14000},
        
        # Bahia - Indústria Química
        {'latitude': -12.9714, 'longitude': -38.5014, 'intensity': 0.85,
         'type': 'chemical', 'name': 'Polo Químico Bahia', 'emission_tons_co2': 10000},
        
        # Santa Catarina - Papel e Celulose
        {'latitude': -27.5954, 'longitude': -48.5480, 'intensity': 0.78,
         'type': 'paper_mill', 'name': 'Fábrica de Celulose SC', 'emission_tons_co2': 8000},
        
        # Amazonas - Garimpo e Desmatamento
        {'latitude': -3.1190, 'longitude': -60.0217, 'intensity': 0.91,
         'type': 'deforestation', 'name': 'Zona de Garimpo Amazonas', 'emission_tons_co2': 13000},
        
        # Tráfego urbano - Região metropolitana SP
        {'latitude': -23.4613, 'longitude': -46.4560, 'intensity': 0.72,
         'type': 'vehicle', 'name': 'Corredor Metropolitano SP', 'emission_tons_co2': 6500},
        
        # Agricultura - Mato Grosso
        {'latitude': -15.8267, 'longitude': -56.0007, 'intensity': 0.68,
         'type': 'agriculture', 'name': 'Zona Agropecuária MT', 'emission_tons_co2': 5500},
        
        # Porto de Santos
        {'latitude': -23.9545, 'longitude': -46.3033, 'intensity': 0.82,
         'type': 'port', 'name': 'Porto de Santos', 'emission_tons_co2': 9200},
        
        # Paraná - Indústria Alimentícia
        {'latitude': -25.4284, 'longitude': -49.2733, 'intensity': 0.65,
         'type': 'food_industry', 'name': 'Polo Alimentício Paraná', 'emission_tons_co2': 5000},
    ]
    
    # Adicionar dados
    generator.add_emission_sources(emission_sources)
    
    # Gerar mapa
    output_file = generator.generate_html_map()
    
    print("\n" + "="*60)
    print("✅ SUCESSO! Abra o arquivo no navegador:")
    print(f"   {output_file}")
    print("="*60)
