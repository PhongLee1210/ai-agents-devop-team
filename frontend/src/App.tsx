import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Header from "./components/Header";

function Home() {
  return (
    <div className="py-12 px-4">
      <h2 className="text-3xl font-bold mb-6 text-center">
        Welcome to DevGenius
      </h2>
      <p className="text-lg text-center max-w-2xl mx-auto">
        A DevOps AI Agent Team designed to streamline your React + Vite +
        TypeScript + Tailwind CSS development workflow
      </p>
      <div className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl mx-auto">
        <FeatureCard
          title="CI/CD Pipelines"
          description="Automated GitHub Actions workflows optimized for frontend development"
          icon="🔄"
        />
        <FeatureCard
          title="Docker Containers"
          description="Containerize your frontend applications with optimized configurations"
          icon="🐳"
        />
        <FeatureCard
          title="Build Prediction"
          description="AI-powered predictions to prevent build failures before they happen"
          icon="🔮"
        />
      </div>
    </div>
  );
}

function About() {
  return (
    <div className="py-12 px-4 max-w-4xl mx-auto">
      <h2 className="text-3xl font-bold mb-6 text-center">About DevGenius</h2>
      <p className="text-lg mb-6">
        DevGenius is a team of AI agents designed to enhance your DevOps
        workflow for modern frontend development using React, Vite, TypeScript,
        and Tailwind CSS.
      </p>
      <p className="text-lg mb-6">
        Our AI agents work together to automate repetitive tasks, provide
        intelligent insights, and optimize your development process from start
        to finish.
      </p>
      <p className="text-lg">
        Built with industry-leading AI technology from GROQ, DevGenius leverages
        large language models to understand your codebase and provide contextual
        assistance.
      </p>
    </div>
  );
}

function Dashboard() {
  return (
    <div className="py-12 px-4 max-w-6xl mx-auto">
      <h2 className="text-3xl font-bold mb-6 text-center">DevOps Dashboard</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h3 className="text-xl font-semibold mb-4">Build Status</h3>
          <div className="flex items-center space-x-2">
            <span className="h-4 w-4 bg-green-500 rounded-full"></span>
            <span>All systems operational</span>
          </div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h3 className="text-xl font-semibold mb-4">Latest Deployment</h3>
          <p>Version: 1.2.0</p>
          <p>Deployed: 2 hours ago</p>
          <p>Status: Successful</p>
        </div>
      </div>
    </div>
  );
}

interface FeatureCardProps {
  title: string;
  description: string;
  icon: string;
}

function FeatureCard({ title, description, icon }: FeatureCardProps) {
  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <div className="text-4xl mb-4">{icon}</div>
      <h3 className="text-xl font-semibold mb-2">{title}</h3>
      <p className="text-gray-600">{description}</p>
    </div>
  );
}

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <Header />
        <main>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/about" element={<About />} />
            <Route path="/dashboard" element={<Dashboard />} />
          </Routes>
        </main>
        <footer className="bg-primary-800 text-white py-6">
          <div className="container mx-auto px-4 text-center">
            <p>© 2023 DevGenius. All rights reserved.</p>
          </div>
        </footer>
      </div>
    </Router>
  );
}

export default App;
