import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import React from "react";
import App from "./App.integration";
import AgentSelector from "./components/AgentSelector";
import Login from "./components/Auth/Login";
import Register from "./components/Auth/Register";
import { ApiProvider } from "./data-provider/simplified-api";

// Mock the useNavigate hook
jest.mock("react-router-dom", () => ({
	...jest.requireActual("react-router-dom"),
	useNavigate: () => jest.fn(),
	BrowserRouter: ({ children }) => <div>{children}</div>,
	Routes: ({ children }) => <div>{children}</div>,
	Route: ({ children }) => <div>{children}</div>,
	Navigate: () => <div>Navigate</div>,
}));

// Mock the API context
jest.mock("./data-provider/simplified-api", () => ({
	ApiProvider: ({ children }) => <div>{children}</div>,
	useApi: () => ({
		login: jest.fn().mockResolvedValue({ access_token: "test-token" }),
		register: jest.fn().mockResolvedValue({ user_id: "123" }),
		getAgents: jest
			.fn()
			.mockResolvedValue([
				{ agent_id: "agent1", name: "Test Agent", agent_type: "sdk" },
			]),
		getAgent: jest.fn().mockResolvedValue({
			agent_id: "agent1",
			name: "Test Agent",
			agent_type: "sdk",
		}),
		getCurrentUser: jest.fn().mockResolvedValue({
			user_id: "123",
			email: "test@example.com",
		}),
	}),
}));

describe("Login Component", () => {
	test("renders login form", () => {
		render(<Login />);

		expect(screen.getByLabelText(/email address/i)).toBeInTheDocument();
		expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
		expect(
			screen.getByRole("button", { name: /sign in/i }),
		).toBeInTheDocument();
	});

	test("handles form submission", async () => {
		render(<Login />);

		fireEvent.change(screen.getByLabelText(/email address/i), {
			target: { value: "test@example.com" },
		});

		fireEvent.change(screen.getByLabelText(/password/i), {
			target: { value: "password123" },
		});

		fireEvent.click(screen.getByRole("button", { name: /sign in/i }));

		// Wait for the form submission to complete
		await waitFor(() => {
			expect(screen.queryByText(/signing in/i)).not.toBeInTheDocument();
		});
	});
});

describe("Register Component", () => {
	test("renders registration form", () => {
		render(<Register />);

		expect(screen.getByLabelText(/email address/i)).toBeInTheDocument();
		expect(screen.getByLabelText(/username/i)).toBeInTheDocument();
		expect(screen.getByLabelText(/^password$/i)).toBeInTheDocument();
		expect(screen.getByLabelText(/confirm password/i)).toBeInTheDocument();
		expect(
			screen.getByRole("button", { name: /register/i }),
		).toBeInTheDocument();
	});

	test("validates password match", async () => {
		render(<Register />);

		fireEvent.change(screen.getByLabelText(/email address/i), {
			target: { value: "test@example.com" },
		});

		fireEvent.change(screen.getByLabelText(/username/i), {
			target: { value: "testuser" },
		});

		fireEvent.change(screen.getByLabelText(/^password$/i), {
			target: { value: "password123" },
		});

		fireEvent.change(screen.getByLabelText(/confirm password/i), {
			target: { value: "password456" },
		});

		fireEvent.click(screen.getByRole("button", { name: /register/i }));

		// Wait for validation error
		await waitFor(() => {
			expect(screen.getByText(/passwords do not match/i)).toBeInTheDocument();
		});
	});
});

describe("AgentSelector Component", () => {
	test("renders agent selector", async () => {
		const onSelect = jest.fn();
		render(<AgentSelector onSelect={onSelect} />);

		// Wait for agents to load
		await waitFor(() => {
			expect(screen.getByText(/select agent/i)).toBeInTheDocument();
		});
	});
});

describe("App Integration", () => {
	test("renders app with authentication flow", () => {
		render(<App />);

		// Initial loading state
		expect(screen.getByText(/loading/i)).toBeInTheDocument();
	});
});
