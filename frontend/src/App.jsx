import React, { useState, useEffect, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import axios from "axios";

const API = "http://localhost:8000";

// --- Reusable UI Components ---
const Spinner = () => (
  <div className="flex items-center justify-center py-12">
    <div className="w-8 h-8 border-3 border-accent-green border-t-transparent rounded-full animate-spin" />
  </div>
);

const SeverityBadge = ({ severity }) => {
  const colors = {
    high: "bg-red-100 text-red-700",
    medium: "bg-amber-100 text-amber-700",
    low: "bg-green-100 text-green-700",
  };
  return (
    <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold uppercase ${colors[severity] || colors.low}`}>
      {severity}
    </span>
  );
};

const TabButton = ({ active, label, icon, onClick }) => (
  <button
    onClick={onClick}
    className={`flex items-center gap-3 px-6 py-4 rounded-2xl font-semibold transition-all duration-200 w-full text-left ${active ? "bg-pill-orange text-text-primary" : "text-text-secondary hover:text-text-primary hover:bg-amber-50/50"
      }`}
  >
    {icon}
    {label}
  </button>
);

// --- ICONS (inline SVGs) ---
const Icons = {
  dashboard: (
    <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
      <path d="M5 3a2 2 0 00-2 2v2a2 2 0 002 2h2a2 2 0 002-2V5a2 2 0 00-2-2H5zM5 11a2 2 0 00-2 2v2a2 2 0 002 2h2a2 2 0 002-2v-2a2 2 0 00-2-2H5zM11 5a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V5zM11 13a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
    </svg>
  ),
  insights: (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" />
    </svg>
  ),
  field: (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" />
    </svg>
  ),
  settings: (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" />
      <path d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" />
    </svg>
  ),
  mail: (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" />
    </svg>
  ),
  logout: (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" />
    </svg>
  ),
  chevron: (
    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path d="M9 5l7 7-7 7" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" />
    </svg>
  ),
};

// =======================================================================
// SECTION: DASHBOARD (Main view with Soil Analysis + Static Insights)
// =======================================================================
const DashboardView = ({ simulation, kpis, isOptimizing }) => {
  const soilMetrics = [
    { label: "Sunlight Level", key: "N", icon: "S", iconBg: "bg-blue-100", iconColor: "text-blue-600", barColor: "bg-blue-400" },
    { label: "Water Level", key: "P", icon: "W", iconBg: "bg-green-100", iconColor: "text-accent-green", barColor: "bg-accent-green" },
    { label: "Soil Nutrients Level", key: "K", icon: "S", iconBg: "bg-lime-100", iconColor: "text-lime-600", barColor: "bg-lime-400" },
    { label: "Plant Health Index", key: "pH", icon: "🌱", iconBg: "bg-yellow-100", iconColor: "text-yellow-600", barColor: "bg-green-500" },
    { label: "Soil Nutrient Balance", key: "moisture", icon: "⚖️", iconBg: "bg-purple-100", iconColor: "text-purple-600", barColor: "bg-purple-500" },
  ];

  const computeAvg = (key) => {
    if (!simulation?.soil_data?.[key]) return 0;
    const data = simulation.soil_data[key];
    const flat = data.flat();
    return (flat.reduce((a, b) => a + b, 0) / flat.length).toFixed(1);
  };

  const parseGridSize = () => {
    if (simulation?.metadata?.grid_size) return simulation.metadata.grid_size;
    return 40;
  };

  const gridSize = parseGridSize();

  const renderGrid = () => {
    const size = gridSize;
    const count = size * size;
    const cells = [];
    for (let i = 0; i < count; i++) {
      const rand = Math.random();
      const isHealthy = isOptimizing ? rand > 0.05 : rand > 0.45;
      const isModerate = !isHealthy && Math.random() > 0.35;
      const colorClass = isHealthy ? "bg-[#5CA278]" : isModerate ? "bg-[#FFC50B]" : "bg-[#F87278]";
      cells.push(<div key={i} className={`w-full aspect-square rounded-[1px] md:rounded-[1px] ${colorClass} transition-colors duration-1000`} />);
    }
    return cells;
  };

  return (
    <div className="grid grid-cols-12 gap-8 flex-grow">
      {/* Left Column: Grid + Chart */}
      <div className="col-span-8 flex flex-col gap-8">

        {/* Root-Zone Optimization Map */}
        <motion.section initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="bg-card-bg rounded-[32px] p-8 border border-gray-100 shadow-sm relative overflow-hidden">
          <div className="flex justify-between items-center mb-6">
            <div>
              <h3 className="text-xl font-bold text-text-primary mb-1">Root-Zone Optimization Map</h3>
              <p className="text-sm text-text-secondary">Real-time heatmap of plant health across grid</p>
            </div>
            <div className="flex gap-4 text-xs font-semibold">
              <span className="flex items-center gap-2"><div className="w-3 h-3 rounded-[3px] bg-[#5CA278]" /> Healthy</span>
              <span className="flex items-center gap-2"><div className="w-3 h-3 rounded-[3px] bg-[#FFC50B]" /> Moderate</span>
              <span className="flex items-center gap-2"><div className="w-3 h-3 rounded-[3px] bg-[#F87278]" /> Deficient</span>
            </div>
          </div>

          <div
            className="grid gap-[1px] md:gap-[2px] bg-white p-2 rounded-[12px] border border-gray-100 shadow-sm overflow-hidden"
            style={{
              gridTemplateColumns: `repeat(${gridSize}, minmax(0, 1fr))`,
              maxHeight: '400px'
            }}
          >
            {renderGrid()}
          </div>

          {/* AI Decisions Panel */}
          <div className="grid grid-cols-3 gap-4 mt-8">
            <div className="bg-red-50/50 rounded-2xl p-4 border border-red-50">
              <p className="text-[10px] font-bold text-text-secondary uppercase tracking-wider">Plants Needing Fertilizer</p>
              <p className="text-2xl font-bold text-red-600 mt-1">{isOptimizing ? "184" : "1,842"}</p>
            </div>
            <div className="bg-green-50/50 rounded-2xl p-4 border border-green-50">
              <p className="text-[10px] font-bold text-text-secondary uppercase tracking-wider">Plants Optimized</p>
              <p className="text-2xl font-bold text-accent-green mt-1">{isOptimizing ? (gridSize * gridSize).toLocaleString() : "2,158"}</p>
            </div>
            <div className="bg-blue-50/50 rounded-2xl p-4 border border-blue-50">
              <p className="text-[10px] font-bold text-text-secondary uppercase tracking-wider">Average Nutrient Deficit</p>
              <p className="text-2xl font-bold text-blue-600 mt-1">{isOptimizing ? "0.2%" : "38%"}</p>
            </div>
          </div>

          {/* AI Simulation Live Status Overlay */}
          {isOptimizing && (
            <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
              className="absolute bottom-4 left-8 right-8 bg-black/85 backdrop-blur-xl rounded-2xl p-6 flex items-center justify-between z-10 border border-white/20 shadow-2xl">
              <div className="flex items-center gap-4">
                <div className="bg-accent-green p-2.5 rounded-xl animate-bounce shadow-lg shadow-green-500/20">🤖</div>
                <div>
                  <p className="text-white font-bold text-base leading-none">ARZIS AI Simulation Active</p>
                  <p className="text-accent-green text-[10px] uppercase font-black tracking-widest mt-1 opacity-80">Optimizing Root-Zone Distribution</p>
                </div>
              </div>
              <div className="flex gap-10 border-l border-white/10 pl-10">
                <div className="text-center">
                  <p className="text-gray-400 text-[10px] font-bold tracking-widest uppercase mb-1">Fertilizer Prescription</p>
                  <p className="text-accent-green font-black text-lg">{(gridSize * 1.84).toFixed(1)} <span className="text-[10px] font-normal opacity-60">kg/ha</span></p>
                </div>
                <div className="text-center">
                  <p className="text-gray-400 text-[10px] font-bold tracking-widest uppercase mb-1">Ideal Water Ratio</p>
                  <p className="text-blue-400 font-black text-lg">0.86 <span className="text-[10px] font-normal opacity-60">(Dynamic)</span></p>
                </div>
              </div>
            </motion.div>
          )}
        </motion.section>

        {/* Crop Health Simulation Chart */}
        <motion.section initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }} className="bg-amber-50/30 border border-amber-100/50 rounded-[32px] p-8">
          <div className="flex justify-between items-center mb-8">
            <h3 className="text-text-primary font-bold">Crop Health Simulation</h3>
            <div className="flex gap-4 text-xs font-semibold">
              <span className="flex items-center gap-2 text-accent-green"><div className="w-3 h-3 rounded-full bg-accent-green" /> ARZIS System</span>
              <span className="flex items-center gap-2 text-accent-orange"><div className="w-3 h-3 rounded-full bg-accent-orange" /> Traditional Farming</span>
            </div>
          </div>
          <div className="relative h-48 w-full mt-4">
            <div className="absolute inset-0 flex flex-col justify-between text-[10px] text-gray-300">
              {[...Array(5)].map((_, i) => <div key={i} className="border-b border-dashed border-gray-200 w-full h-0" />)}
            </div>
            <svg className="absolute inset-0 w-full h-full overflow-visible" preserveAspectRatio="none">
              <path className="stroke-accent-orange stroke-[3px] fill-transparent" d="M0,120 C100,100 150,150 250,130 S400,160 600,140" strokeLinecap="round" />
              <path className="stroke-accent-green stroke-[4px] fill-transparent transition-all duration-1000" d={isOptimizing ? "M0,150 C50,180 150,50 250,30 S450,10 600,0" : "M0,150 C50,180 150,50 250,100 S450,80 600,70"} strokeLinecap="round" />
            </svg>
          </div>
          <div className="flex justify-between mt-4 text-[11px] text-text-secondary px-2">
            <span>Week 1</span><span>Week 2</span><span>Week 3</span><span>Week 4</span><span>Week 5</span><span>Week 6</span><span>Week 7</span>
          </div>
        </motion.section>
      </div>

      {/* Right Column: NPK Soil Balance + Insights */}
      <div className="col-span-4 flex flex-col gap-8">

        {/* NPK Soil Balance */}
        <motion.section initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
          <div className="flex justify-between items-center mb-6">
            <h3 className="text-xl font-bold text-text-primary">NPK Soil Balance</h3>
          </div>
          <div className="space-y-6 bg-card-bg p-6 rounded-[24px] border border-gray-100 shadow-sm">
            {soilMetrics.map((m, idx) => {
              const val = parseFloat(computeAvg(m.key)) || 50;
              const finalVal = isOptimizing ? val * 1.4 : val;
              const pctWidth = `${Math.min((finalVal / 200) * 100, 100)}%`;
              return (
                <div key={m.key} className="flex items-center gap-4">
                  <div className={`w-12 h-12 ${m.iconBg} ${m.iconColor} font-bold flex items-center justify-center rounded-2xl text-lg shadow-sm`}>{m.icon}</div>
                  <div className="flex-grow">
                    <p className="text-sm font-semibold mb-2">{m.label}</p>
                    <div className="w-full bg-gray-100 rounded-full h-2 overflow-hidden">
                      <div style={{ width: m.key === 'moisture' ? '80%' : pctWidth }} className={`h-full ${m.barColor} transition-all duration-1000`} />
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </motion.section>

        {/* ARZIS AI Insights */}
        <motion.section initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }} className="mt-4 flex-grow flex flex-col">
          <h3 className="text-xl font-bold text-text-primary mb-6">ARZIS AI Insights</h3>
          <div className="space-y-4 flex-grow">
            {[
              { color: "text-accent-green", bg: "bg-green-100", title: "Fertilizer Optimization", desc: `AI reduced fertilizer use by ${isOptimizing ? "34.5%" : "21.8%"} while maintaining crop health at optimal levels.` },
              { color: "text-accent-orange", bg: "bg-orange-100", title: "Nutrient Hotspots", desc: "183 plants identified with critical nitrogen deficiency. Dosing scheduled." },
              { color: "text-blue-500", bg: "bg-blue-100", title: "Adaptive Strategy", desc: `Targeted fertilization dynamically applied to only ${isOptimizing ? "4.2%" : "7.4%"} of grid plants today.` },
            ].map((item, idx) => (
              <div key={idx} className="bg-card-bg p-5 rounded-[24px] shadow-sm border border-gray-100 flex gap-4">
                <div className={`mt-1 ${item.bg} p-2.5 rounded-2xl h-fit ${item.color}`}>
                  <svg className="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>
                </div>
                <div>
                  <h4 className="font-bold text-text-primary text-sm mb-1.5">{item.title}</h4>
                  <p className="text-xs text-text-secondary leading-relaxed">{item.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </motion.section>
      </div>
    </div>
  );
};

// =======================================================================
// SECTION: INSIGHTS (AI-driven recommendations from backend)
// =======================================================================
const InsightsView = ({ insights, loading }) => {
  if (loading) return <Spinner />;

  const categoryIcons = {
    "Water Optimization": "💧",
    "Irrigation Efficiency": "🚿",
    "Soil Acidity": "⚗️",
    "Sun Rays Ratio": "☀️",
    "Crop Performance": "🌾",
    "Magnesium Levels": "🧲",
    "Water Level": "🌊",
    "Nutrient Level": "🧬",
    "Humidity Level": "☁️",
  };

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.4 }}>
      <h3 className="text-2xl font-bold text-text-primary mb-2">AI-Driven Insights</h3>
      <p className="text-sm text-text-secondary mb-8">Real-time recommendations from the ARZIS simulation engine and RL agent.</p>

      {insights.length === 0 ? (
        <div className="bg-green-50 p-8 rounded-[24px] text-center">
          <p className="text-lg font-semibold text-accent-green">✅ All systems optimal</p>
          <p className="text-sm text-text-secondary mt-2">No alerts or recommendations at this time.</p>
        </div>
      ) : (
        <div className="space-y-5">
          {insights.map((insight, idx) => (
            <motion.div
              key={insight.id}
              initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.08 * idx, duration: 0.4 }}
              className={`bg-card-bg rounded-[24px] p-6 border shadow-sm ${insight.severity === "high" ? "border-red-200" : insight.severity === "medium" ? "border-amber-200" : "border-gray-100"
                }`}
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  <span className="text-2xl">{categoryIcons[insight.category] || "📊"}</span>
                  <div>
                    <h4 className="font-bold text-text-primary">{insight.category}</h4>
                    <p className="text-[11px] text-text-secondary">{new Date(insight.timestamp).toLocaleString()}</p>
                  </div>
                </div>
                <SeverityBadge severity={insight.severity} />
              </div>

              <div className="grid grid-cols-3 gap-4 mt-4">
                <div className="bg-amber-50/50 rounded-2xl p-4">
                  <p className="text-[10px] font-semibold text-text-secondary uppercase mb-1">Observation</p>
                  <p className="text-sm text-text-primary leading-relaxed">{insight.observation}</p>
                </div>
                <div className="bg-green-50/50 rounded-2xl p-4">
                  <p className="text-[10px] font-semibold text-text-secondary uppercase mb-1">AI Recommendation</p>
                  <p className="text-sm text-text-primary leading-relaxed">{insight.recommendation}</p>
                </div>
                <div className="bg-blue-50/50 rounded-2xl p-4">
                  <p className="text-[10px] font-semibold text-text-secondary uppercase mb-1">Expected Benefit</p>
                  <p className="text-sm text-text-primary font-semibold leading-relaxed">{insight.expected_benefit}</p>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      )}
    </motion.div>
  );
};

// =======================================================================
// SECTION: FIELD / CUSTOMER DETAILS
// =======================================================================
const FieldDetailsView = ({ farmer, field, loading }) => {
  if (loading) return <Spinner />;

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.4 }}>
      <h3 className="text-2xl font-bold text-text-primary mb-2">Field & Customer Details</h3>
      <p className="text-sm text-text-secondary mb-8">Farm profile, field metadata, and yield history.</p>

      <div className="grid grid-cols-2 gap-6">
        {/* Farmer Profile */}
        <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}
          className="bg-card-bg rounded-[24px] p-6 border border-gray-100 shadow-sm">
          <h4 className="font-bold text-text-primary mb-4 flex items-center gap-2">
            <span className="w-8 h-8 bg-accent-green/10 text-accent-green rounded-full flex items-center justify-center text-sm">👤</span>
            Farmer Profile
          </h4>
          {farmer ? (
            <div className="space-y-3">
              <InfoRow label="Name" value={farmer.name} />
              <InfoRow label="Email" value={farmer.email} />
              <InfoRow label="Phone" value={farmer.phone} />
              <div className="pt-3 border-t border-gray-50 mt-2">
                <span className="text-[10px] uppercase font-bold text-accent-green bg-green-50 px-2.5 py-1 rounded-md">Verified Farmer</span>
              </div>
            </div>
          ) : (
            <div className="space-y-3">
              <InfoRow label="Name" value="John Doe" />
              <InfoRow label="Email" value="john.doe@farmtech.io" />
              <InfoRow label="Phone" value="+1 555-0198" />
            </div>
          )}
        </motion.div>

        {/* Location & Metadata */}
        <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15 }}
          className="bg-card-bg rounded-[24px] p-6 border border-gray-100 shadow-sm">
          <h4 className="font-bold text-text-primary mb-4 flex items-center gap-2">
            <span className="w-8 h-8 bg-accent-orange/10 text-accent-orange rounded-full flex items-center justify-center text-sm">📍</span>
            Location & Metadata
          </h4>
          {field ? (
            <div className="space-y-3">
              <InfoRow label="Field Name" value={field.name} />
              <InfoRow label="Area" value={`${field.area_hectares} ha`} />
              <InfoRow label="Crop" value={field.crop_type} />
              <InfoRow label="Coordinates" value={`${field.latitude}°N, ${field.longitude}°W`} />
            </div>
          ) : (
            <div className="space-y-3">
              <InfoRow label="Field Name" value="Sector A - North" />
              <InfoRow label="Area" value="150.0 ha" />
              <InfoRow label="Crop" value="Corn" />
              <InfoRow label="Coordinates" value="41.87°N, 87.62°W" />
            </div>
          )}
        </motion.div>

        {/* Soil Data */}
        <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}
          className="bg-card-bg rounded-[24px] p-6 border border-gray-100 shadow-sm">
          <h4 className="font-bold text-text-primary mb-4 flex items-center gap-2">
            <span className="w-8 h-8 bg-yellow-100 text-yellow-600 rounded-full flex items-center justify-center text-sm">🌱</span>
            Field Soil Data
          </h4>
          {(field || { soil_rating: "Excellent", current_moisture_level: 65.4 }) ? (
            <div className="space-y-3">
              <InfoRow label="Soil Rating" value={field?.soil_rating || "Excellent"} />
              <InfoRow label="Current Moisture" value={`${field?.current_moisture_level || 65.4}%`} />
              <div className="mt-3">
                <div className="flex justify-between text-[11px] text-text-secondary mb-1">
                  <span>Moisture Level</span>
                  <span>{field?.current_moisture_level || 65.4}%</span>
                </div>
                <div className="w-full bg-gray-100 rounded-full h-2">
                  <div className="bg-accent-green rounded-full h-2 transition-all duration-700" style={{ width: `${field?.current_moisture_level || 65.4}%` }} />
                </div>
              </div>
            </div>
          ) : <p className="text-sm text-text-secondary">No soil data</p>}
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.25 }}
          className="bg-card-bg rounded-[24px] p-6 border border-gray-100 shadow-sm">
          <h4 className="font-bold text-text-primary mb-4 flex items-center gap-2">
            <span className="w-8 h-8 bg-green-100 text-green-600 rounded-full flex items-center justify-center text-sm">📊</span>
            Yield History
          </h4>
          <div className="space-y-3">
            {(field?.yield_history || [
              { year: 2024, crop: "Corn", yield_tons_per_ha: 11.2 },
              { year: 2023, crop: "Soybeans", yield_tons_per_ha: 4.5 },
              { year: 2022, crop: "Corn", yield_tons_per_ha: 10.8 }
            ]).map((yh, i) => (
              <div key={i} className="flex items-center justify-between py-2 border-b border-gray-50 last:border-0">
                <div>
                  <p className="text-sm font-semibold text-text-primary">{yh.crop}</p>
                  <p className="text-[11px] text-text-secondary">{yh.year}</p>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-20 bg-gray-100 rounded-full h-1.5">
                    <div className="bg-accent-green rounded-full h-1.5" style={{ width: `${(yh.yield_tons_per_ha / 15) * 100}%` }} />
                  </div>
                  <span className="text-sm font-bold text-text-primary">{yh.yield_tons_per_ha} t/ha</span>
                </div>
              </div>
            ))}
          </div>
        </motion.div>
      </div>
    </motion.div>
  );
};

const InfoRow = ({ label, value }) => (
  <div className="flex justify-between items-center">
    <span className="text-xs text-text-secondary">{label}</span>
    <span className="text-sm font-semibold text-text-primary">{value}</span>
  </div>
);

const SelectField = ({ label, value, options, onChange }) => (
  <div className="flex flex-col gap-2">
    <label className="text-xs text-text-secondary font-semibold uppercase tracking-wider">{label}</label>
    <select
      value={value}
      onChange={(e) => onChange(e.target.value)}
      className="bg-gray-50 border border-gray-200 text-text-primary text-sm rounded-xl focus:ring-accent-green focus:border-accent-green block w-full p-3 font-medium outline-none transition-all"
    >
      {options.map(opt => (
        <option key={opt} value={opt}>{opt}</option>
      ))}
    </select>
  </div>
);

const DateField = ({ label, value, onChange }) => (
  <div className="flex flex-col gap-2">
    <label className="text-xs text-text-secondary font-semibold uppercase tracking-wider">{label}</label>
    <input
      type="date"
      value={value || ""}
      onChange={(e) => onChange(e.target.value)}
      className="bg-gray-50 border border-gray-200 text-text-primary text-sm rounded-xl focus:ring-accent-green focus:border-accent-green block w-full p-3 font-medium outline-none transition-all"
    />
  </div>
);

const SliderField = ({ label, value, min, max, step = 1, onChange }) => (
  <div>
    <div className="flex justify-between text-xs mb-2">
      <span className="text-text-secondary font-semibold uppercase tracking-wider">{label}</span>
      <span className="font-bold text-text-primary">{typeof value === "number" ? (Number.isInteger(step) ? value : value.toFixed(1)) : value}</span>
    </div>
    <input type="range" min={min} max={max} step={step} value={value}
      onChange={e => onChange(Number(e.target.value))}
      className="w-full h-1.5 bg-gray-200 rounded-full appearance-none cursor-pointer accent-accent-green" />
  </div>
);

const ToggleField = ({ label, value, options, onChange }) => (
  <div>
    <p className="text-xs text-text-secondary font-semibold uppercase tracking-wider mb-2">{label}</p>
    <div className="flex gap-2 flex-wrap">
      {options.map(opt => (
        <button key={opt} onClick={() => onChange(opt)}
          className={`px-4 py-2 rounded-xl text-xs font-semibold transition-all ${value === opt ? "bg-accent-green text-white shadow-sm" : "bg-gray-100 text-text-secondary hover:bg-gray-200"
            }`}>
          {opt.charAt(0).toUpperCase() + opt.slice(1)}
        </button>
      ))}
    </div>
  </div>
);

// =======================================================================
// SECTION: CUSTOMIZATION CONTROLS
// =======================================================================
const CustomizationView = ({ preferences, onSave, loading, saving }) => {
  const [form, setForm] = useState(null);

  useEffect(() => {
    if (preferences) {
      setForm({
        ...preferences,
        grid_size: preferences.grid_size || "40x40",
        crop_type: preferences.crop_type || "Corn",
        planting_date: preferences.planting_date || "2024-03-01",
      });
    }
  }, [preferences]);

  if (loading || !form) return <Spinner />;

  const update = (key, val) => setForm(prev => ({ ...prev, [key]: val }));

  const handleSave = () => onSave(form);

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.4 }}>
      <div className="flex items-center justify-between mb-8">
        <div>
          <h3 className="text-2xl font-bold text-text-primary">Simulation Settings</h3>
          <p className="text-sm text-text-secondary">Configure field parameters, crop types, and simulation alerts.</p>
        </div>
        <button onClick={handleSave} disabled={saving}
          className="bg-accent-green text-white px-6 py-3 rounded-xl font-semibold hover:bg-opacity-90 transition-all disabled:opacity-50 flex items-center gap-2 shadow-md">
          {saving ? "Saving..." : "Save Preferences"}
        </button>
      </div>

      <div className="grid grid-cols-2 gap-8">
        {/* Field & Crop Configuration */}
        <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}
          className="bg-card-bg rounded-[32px] p-8 border border-gray-100 shadow-sm">
          <h4 className="font-bold text-text-primary mb-6 flex items-center gap-2 text-lg">
            <span className="text-xl">🚜</span> Field & Crop Params
          </h4>
          <div className="space-y-6">
            <SelectField
              label="Grid Size (Plants)"
              value={form.grid_size}
              options={["20x20", "30x30", "40x40", "50x50"]}
              onChange={v => update("grid_size", v)}
            />
            <SelectField
              label="Select Crop Type"
              value={form.crop_type}
              options={["Corn", "Wheat", "Soybean", "Rice", "Cotton"]}
              onChange={v => update("crop_type", v)}
            />
            <DateField
              label="When it was planted"
              value={form.planting_date}
              onChange={v => update("planting_date", v)}
            />
          </div>
        </motion.div>

        {/* Irrigation & Water */}
        <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15 }}
          className="bg-card-bg rounded-[32px] p-8 border border-gray-100 shadow-sm">
          <h4 className="font-bold text-text-primary mb-6 flex items-center gap-2 text-lg">
            <span className="text-xl">💧</span> Irrigation & Water
          </h4>
          <div className="space-y-6">
            <ToggleField label="Irrigation Mode" value={form.irrigation_mode} options={["auto", "manual"]} onChange={v => update("irrigation_mode", v)} />
            <SliderField label="Daily Water Limit (liters)" value={form.daily_water_limit_liters} min={0} max={50000} step={500} onChange={v => update("daily_water_limit_liters", v)} />
          </div>
        </motion.div>

        {/* Notifications */}
        <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}
          className="bg-card-bg rounded-[32px] p-8 border border-gray-100 shadow-sm">
          <h4 className="font-bold text-text-primary mb-6 flex items-center gap-2 text-lg">
            <span className="text-xl">📬</span> Notifications
          </h4>
          <div className="space-y-6">
            <ToggleField label="Notification Method" value={form.notification_method} options={["in-app", "email", "sms"]} onChange={v => update("notification_method", v)} />
          </div>
        </motion.div>

        {/* System Preferences */}
        <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.25 }}
          className="bg-card-bg rounded-[32px] p-8 border border-gray-100 shadow-sm">
          <h4 className="font-bold text-text-primary mb-6 flex items-center gap-2 text-lg">
            <span className="text-xl">⚙️</span> System Preferences
          </h4>
          <div className="space-y-6">
            <ToggleField label="Theme" value={form.theme} options={["dark", "light"]} onChange={v => update("theme", v)} />
            <ToggleField label="Units" value={form.units} options={["metric", "imperial"]} onChange={v => update("units", v)} />
            <ToggleField label="Language" value={form.language} options={["en", "es", "fr", "de", "hi"]} onChange={v => update("language", v)} />
          </div>
        </motion.div>
      </div>
    </motion.div>
  );
};

// =======================================================================
// MAIN APP
// =======================================================================
const App = () => {
  const [activeTab, setActiveTab] = useState("dashboard");
  const [simulation, setSimulation] = useState(null);
  const [insights, setInsights] = useState([]);
  const [farmer, setFarmer] = useState({
    name: "John Doe",
    email: "john.doe@farmtech.io",
    phone: "+1 555-0198"
  });
  const [field, setField] = useState({
    name: "Sector A - North",
    area_hectares: 150.0,
    crop_type: "Corn",
    latitude: 41.8781,
    longitude: -87.6298,
    soil_rating: "Excellent",
    current_moisture_level: 65.4,
    yield_history: [
      { year: 2024, crop: "Corn", yield_tons_per_ha: 11.2 },
      { year: 2023, crop: "Soybeans", yield_tons_per_ha: 4.5 },
      { year: 2022, crop: "Corn", yield_tons_per_ha: 10.8 }
    ]
  });
  const [preferences, setPreferences] = useState({
    grid_size: "40x40",
    crop_type: "Corn",
    planting_date: "2024-03-01",
    theme: "light",
    irrigation_mode: "auto",
    daily_water_limit_liters: 10000,
    notification_method: "in-app",
    units: "metric",
    language: "en"
  });
  const [loading, setLoading] = useState({});
  const [saving, setSaving] = useState(false);
  const [isOptimizing, setIsOptimizing] = useState(false);

  const setLoadingKey = (key, val) => setLoading(prev => ({ ...prev, [key]: val }));

  // Initial Fetch: Preferences on mount
  useEffect(() => {
    setLoadingKey("prefs", true);
    axios.get(`${API}/preferences/1`)
      .then(res => setPreferences(res.data))
      .catch(() => { })
      .finally(() => setLoadingKey("prefs", false));
  }, []);

  // Fetch simulation data (Depends on preferences)
  useEffect(() => {
    if (!preferences?.grid_size) return;

    // Parse grid size (e.g. "40x40" -> 40)
    const size = parseInt(preferences.grid_size.split('x')[0]) || 40;
    setLoadingKey("simulation", true);
    axios.get(`${API}/field/simulation?grid_size=${size}`)
      .then(res => setSimulation(res.data))
      .catch(() => {
        // FALLBACK: Generate mock simulation if API fails (for demo)
        setSimulation({
          metadata: { grid_size: size },
          kpis: {
            yield: 12.5,
            nitrogen: 85.0,
            phosphorus: 42.0,
            potassium: 110.0,
            moisture: 68.0,
            ph: 6.8
          }
        });
      })
      .finally(() => setLoadingKey("simulation", false));
  }, [preferences?.grid_size]);

  // Fetch farmer and field on mount
  useEffect(() => {
    setLoadingKey("field", true);
    Promise.all([
      axios.get(`${API}/customer/1`),
      axios.get(`${API}/field/1/details`),
    ]).then(([fRes, fdRes]) => {
      setFarmer(fRes.data);
      setField(fdRes.data);
    }).catch(() => { }).finally(() => setLoadingKey("field", false));
  }, []);

  // Fetch preferences (On tab change to customization to ensure it's fresh)
  useEffect(() => {
    if (activeTab === "customization") {
      setLoadingKey("prefs", true);
      axios.get(`${API}/preferences/1`)
        .then(res => setPreferences(res.data))
        .catch(() => { })
        .finally(() => setLoadingKey("prefs", false));
    }
  }, [activeTab]);

  // Fetch insights (Depends on preferences)
  useEffect(() => {
    if (activeTab === "insights" && preferences?.grid_size) {
      const size = parseInt(preferences.grid_size.split('x')[0]) || 40;
      setLoadingKey("insights", true);
      axios.get(`${API}/insights?grid_size=${size}`)
        .then(res => {
          setInsights(res.data);
          setLoadingKey("insights", false);
        })
        .catch(() => { setLoadingKey("insights", false); });
    }
  }, [activeTab, preferences?.grid_size]);

  // Handle Theme
  useEffect(() => {
    if (preferences?.theme === "dark") {
      document.documentElement.classList.add("dark");
    } else {
      document.documentElement.classList.remove("dark");
    }
  }, [preferences?.theme]);

  // Save preferences and redirect
  const handleSavePreferences = useCallback(async (formData) => {
    setSaving(true);
    try {
      const res = await axios.patch(`${API}/customize/1`, formData);
      setPreferences(res.data);
    } catch (e) {
      // For demo: Update local state even if API fails
      setPreferences(formData);
    } finally {
      // Automatically redirect to the Root-Zone map (Dashboard)
      setActiveTab("dashboard");
      setSaving(false);
    }
  }, [setActiveTab]);

  const kpis = simulation?.kpis;
  const gridSize = simulation?.metadata?.grid_size || 40;

  return (
    <main className={`dashboard-container bg-dashboard-bg w-full rounded-[40px] shadow-2xl flex overflow-hidden transition-colors duration-500 ${preferences?.theme === "dark" ? "dark" : ""}`}>
      {/* Sidebar */}
      <aside className="w-72 bg-sidebar-bg flex flex-col p-8 border-r border-gray-100" data-purpose="sidebar">
        {/* Profile */}
        <div className="flex flex-col items-center mb-10">
          <div className="flex justify-between w-full mb-4">
            <span className="text-xs font-semibold text-accent-green bg-green-50 px-2 py-1 rounded-full">Active</span>
            <button className="text-gray-400">•••</button>
          </div>
          <div className="w-28 h-28 bg-gradient-to-br from-accent-green/20 to-accent-orange/20 rounded-2xl flex items-center justify-center overflow-hidden mb-4">
            <span className="text-4xl">👨‍🌾</span>
          </div>
          <h2 className="text-xl font-bold text-text-primary">{farmer?.name || "John Doe"}</h2>
          <p className="text-sm text-text-secondary">{farmer?.email || "john.doe@farmtech.io"}</p>
        </div>

        {/* Nav */}
        <nav className="flex-grow space-y-2">
          <TabButton active={activeTab === "dashboard"} label="Root-Zone Map" icon={Icons.dashboard} onClick={() => setActiveTab("dashboard")} />
          <TabButton active={activeTab === "insights"} label="AI Optimization" icon={Icons.insights} onClick={() => setActiveTab("insights")} />
          <TabButton active={activeTab === "field"} label="Field Analytics" icon={Icons.field} onClick={() => setActiveTab("field")} />
          <TabButton active={activeTab === "customization"} label="Simulation Settings" icon={Icons.settings} onClick={() => setActiveTab("customization")} />
        </nav>

        {/* Contact */}
        <div className="mt-auto bg-amber-50 p-6 rounded-3xl text-center">
          <div className="bg-gray-700 w-10 h-10 rounded-full flex items-center justify-center mx-auto mb-4 text-white">{Icons.mail}</div>
          <p className="text-xs text-text-secondary leading-relaxed mb-4">Need any help? Our experts would be happy to help!</p>
          <button className="w-full bg-accent-green text-white py-3 rounded-xl font-semibold hover:bg-opacity-90 transition-all">Contact us</button>
        </div>

        {/* Logout */}
        <button className="mt-8 flex items-center gap-3 text-text-secondary hover:text-red-500 transition-colors px-6">
          {Icons.logout} Logout
        </button>
      </aside>

      {/* Main Content */}
      <div className="flex-grow flex flex-col p-10 overflow-y-auto max-h-screen" data-purpose="content-area">
        {/* ARZIS Main Header */}
        <header className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-extrabold text-text-primary mb-1 tracking-tight">ARZIS – Adaptive Root-Zone Intelligence System</h1>
            <p className="text-text-secondary font-medium">AI-powered plant-level fertilizer optimization</p>
          </div>
          <button
            onClick={() => setIsOptimizing(prev => !prev)}
            className={`px-6 py-3.5 rounded-full font-bold text-white transition-all duration-300 shadow-md flex items-center gap-2 ${isOptimizing ? 'bg-amber-500 animate-pulse' : 'bg-accent-green hover:bg-opacity-90 hover:scale-[1.02]'}`}>
            {isOptimizing ? '⚡ Running AI Optimization...' : '🤖 Run AI Optimization'}
          </button>
        </header>

        {/* Top KPI Header */}
        <div className="grid grid-cols-4 gap-6 bg-white p-6 rounded-[24px] shadow-sm border border-gray-100 mb-10">
          <div className="border-r border-gray-100">
            <p className="text-xs font-bold text-text-secondary uppercase mb-1 tracking-wider">Field Size</p>
            <p className="text-2xl font-bold text-text-primary">{field?.area_hectares || "150"} ha</p>
          </div>
          <div className="border-r border-gray-100">
            <p className="text-xs font-bold text-text-secondary uppercase mb-1 tracking-wider">Plants Simulated</p>
            <p className="text-2xl font-bold text-text-primary">{isOptimizing ? (gridSize * gridSize).toLocaleString() : (gridSize * gridSize * 0.6).toLocaleString()}</p>
          </div>
          <div className="border-r border-gray-100">
            <p className="text-xs font-bold text-text-secondary uppercase mb-1 tracking-wider">Fertilizer Saved</p>
            <p className="text-2xl font-bold text-accent-green">{isOptimizing ? "34.5%" : "21.8%"}</p>
          </div>
          <div>
            <p className="text-xs font-bold text-text-secondary uppercase mb-1 tracking-wider">Yield Gain</p>
            <p className="text-2xl font-bold text-accent-green">{isOptimizing ? "+18%" : "+12%"}</p>
          </div>
        </div>

        {/* View Router */}
        <AnimatePresence mode="wait">
          {activeTab === "dashboard" && <DashboardView key="dash" simulation={simulation} kpis={kpis} isOptimizing={isOptimizing} />}
          {activeTab === "insights" && <InsightsView key="ins" insights={insights} loading={loading.insights} />}
          {activeTab === "field" && <FieldDetailsView key="fld" farmer={farmer} field={field} loading={loading.field} />}
          {activeTab === "customization" && <CustomizationView key="cust" preferences={preferences} onSave={handleSavePreferences} loading={loading.prefs} saving={saving} />}
        </AnimatePresence>
      </div>
    </main>
  );
};

export default App;
