'use client';

import React from 'react';
import { Shield, Zap, FileText } from 'lucide-react';

interface FeatureCardProps {
  icon: React.ComponentType<{ className?: string }>;
  title: string;
  description: string;
  iconColor: string;
}

const FeatureCard: React.FC<FeatureCardProps> = ({
  icon: Icon,
  title,
  description,
  iconColor,
}) => (
  <div className="bg-black/30 backdrop-blur-sm p-8 rounded-xl border border-white/10 hover:border-purple-400/50 transition-all duration-300 hover:transform hover:scale-105">
    <div className="bg-black/40 p-4 rounded-lg w-fit mb-6">
      <Icon className={`h-8 w-8 ${iconColor}`} />
    </div>
    <h3 className="text-xl font-semibold text-white mb-3">{title}</h3>
    <p className="text-purple-200">{description}</p>
  </div>
);

const FEATURES = [
  {
    icon: Shield,
    title: 'Risk Detection',
    description:
      'Advanced AI identifies potential legal risks and unfavorable terms',
    iconColor: 'text-blue-500',
  },
  {
    icon: Zap,
    title: 'Instant Analysis',
    description: 'Get comprehensive contract analysis in seconds, not hours',
    iconColor: 'text-yellow-500',
  },
  {
    icon: FileText,
    title: 'Smart Summaries',
    description: 'Clear, actionable insights with highlighted key clauses',
    iconColor: 'text-green-500',
  },
] as const;

const FeaturesGrid: React.FC = () => {
  return (
    <section className="mb-12">
      <div className="max-w-7xl mx-auto px-4">
        <div className="grid md:grid-cols-3 gap-8">
          {FEATURES.map((feature) => (
            <FeatureCard
              key={feature.title}
              icon={feature.icon}
              title={feature.title}
              description={feature.description}
              iconColor={feature.iconColor}
            />
          ))}
        </div>
      </div>
    </section>
  );
};

export default FeaturesGrid;
