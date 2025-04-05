#!/bin/bash

# Script to preserve LibreChat UI components for future use in Atlas-Chat
# This script identifies, backs up, and organizes LibreChat UI components

echo "Starting LibreChat UI preservation process..."

# Create a preservation directory
PRESERVATION_DIR="./librechat_ui_components"
mkdir -p $PRESERVATION_DIR

echo "Created preservation directory: $PRESERVATION_DIR"

# Function to copy a component to the preservation directory
preserve_component() {
	local source=$1
	local target="$PRESERVATION_DIR/$(dirname $source)"

	mkdir -p "$target"
	cp -r "$source" "$target/"

	echo "Preserved: $source"
}

# Function to create a component manifest
create_manifest() {
	local manifest="$PRESERVATION_DIR/manifest.json"
	local components=()

	# Find all preserved components
	while IFS= read -r file; do
		if [[ $file == *.jsx || $file == *.tsx || $file == *.js || $file == *.ts ]]; then
			components+=("$(realpath --relative-to=$PRESERVATION_DIR $file)")
		fi
	done < <(find $PRESERVATION_DIR -type f | sort)

	# Create JSON manifest
	echo "{" >$manifest
	echo '  "name": "LibreChat UI Components",' >>$manifest
	echo '  "description": "Preserved UI components from LibreChat for potential future use in Atlas-Chat",' >>$manifest
	echo "  \"date\": \"$(date +%Y-%m-%d)\"," >>$manifest
	echo '  "components": [' >>$manifest

	for ((i = 0; i < ${#components[@]}; i++)); do
		echo "    \"${components[$i]}\"$(if [[ $i -lt $((${#components[@]} - 1)) ]]; then echo ","; fi)" >>$manifest
	done

	echo "  ]" >>$manifest
	echo "}" >>$manifest

	echo "Created component manifest: $manifest"
}

# Function to preserve valuable UI components
preserve_ui_components() {
	echo "Preserving valuable LibreChat UI components..."

	# Define the source directory for LibreChat components
	FRONTEND_DIR="./frontend/client/src"

	# List of valuable LibreChat UI components to preserve
	VALUABLE_COMPONENTS=(
		# Chat components
		"components/Chat/ChatMessage"
		"components/Chat/Messages"
		"components/Chat/Input"
		"components/Chat/Conversation"
		"components/Chat/ChatBar"
		"components/Chat/Markdown"
		"components/Chat/CodeBlock"

		# UI components
		"components/UI/Dropdown"
		"components/UI/Modal"
		"components/UI/Tooltip"
		"components/UI/Popover"
		"components/UI/Button"
		"components/UI/Card"
		"components/UI/Avatar"
		"components/UI/Icons"

		# Settings components
		"components/Settings/SettingsDialog"
		"components/Settings/SettingsOption"
		"components/Settings/ThemeSelector"

		# Auth components
		"components/Auth/Login"
		"components/Auth/Register"
		"components/Auth/ForgotPassword"

		# Layout components
		"components/Layout/Sidebar"
		"components/Layout/Header"
		"components/Layout/Footer"
		"components/Layout/Main"

		# Utility functions
		"utils/markdown"
		"utils/theme"
		"utils/storage"
		"utils/auth"
		"utils/chat"

		# Hooks
		"hooks/useLocalStorage"
		"hooks/useMediaQuery"
		"hooks/useDebounce"
		"hooks/useTheme"
	)

	# Preserve each component
	for component in "${VALUABLE_COMPONENTS[@]}"; do
		component_path="$FRONTEND_DIR/$component"

		# Check if it's a directory or file
		if [ -d "$component_path" ]; then
			# Preserve the entire directory
			preserve_component "$component_path"
		elif [ -f "$component_path.jsx" ]; then
			preserve_component "$component_path.jsx"
		elif [ -f "$component_path.tsx" ]; then
			preserve_component "$component_path.tsx"
		elif [ -f "$component_path.js" ]; then
			preserve_component "$component_path.js"
		elif [ -f "$component_path.ts" ]; then
			preserve_component "$component_path.ts"
		else
			# Try to find files that match the pattern
			find "$FRONTEND_DIR" -path "*$component*" -name "*.jsx" -o -name "*.tsx" -o -name "*.js" -o -name "*.ts" | while read file; do
				preserve_component "$file"
			done
		fi
	done
}

# Function to preserve styles
preserve_styles() {
	echo "Preserving LibreChat styles..."

	# Define the source directory for LibreChat styles
	STYLES_DIR="./frontend/client/src/styles"

	# Create styles directory in preservation directory
	mkdir -p "$PRESERVATION_DIR/styles"

	# Copy all CSS and SCSS files
	find $STYLES_DIR -name "*.css" -o -name "*.scss" | while read file; do
		preserve_component "$file"
	done

	# Copy tailwind configuration if it exists
	if [ -f "./frontend/client/tailwind.config.js" ]; then
		preserve_component "./frontend/client/tailwind.config.js"
	fi
}

# Function to preserve theme configurations
preserve_themes() {
	echo "Preserving LibreChat themes..."

	# Define the source directory for LibreChat themes
	THEMES_DIR="./frontend/client/src/themes"

	# Create themes directory in preservation directory
	mkdir -p "$PRESERVATION_DIR/themes"

	# Copy all theme files
	if [ -d "$THEMES_DIR" ]; then
		find $THEMES_DIR -type f | while read file; do
			preserve_component "$file"
		done
	fi
}

# Function to create documentation
create_documentation() {
	echo "Creating documentation for preserved components..."

	# Create documentation file
	DOC_FILE="$PRESERVATION_DIR/README.md"

	echo "# LibreChat UI Components" >$DOC_FILE
	echo "" >>$DOC_FILE
	echo "This directory contains UI components preserved from LibreChat for potential future use in Atlas-Chat." >>$DOC_FILE
	echo "" >>$DOC_FILE
	echo "## Component Categories" >>$DOC_FILE
	echo "" >>$DOC_FILE
	echo "### Chat Components" >>$DOC_FILE
	echo "Components related to chat functionality, message rendering, and conversation management." >>$DOC_FILE
	echo "" >>$DOC_FILE
	echo "### UI Components" >>$DOC_FILE
	echo "Reusable UI elements like buttons, dropdowns, modals, etc." >>$DOC_FILE
	echo "" >>$DOC_FILE
	echo "### Settings Components" >>$DOC_FILE
	echo "Components for user settings and preferences." >>$DOC_FILE
	echo "" >>$DOC_FILE
	echo "### Auth Components" >>$DOC_FILE
	echo "Components for authentication and user management." >>$DOC_FILE
	echo "" >>$DOC_FILE
	echo "### Layout Components" >>$DOC_FILE
	echo "Components for page layout and structure." >>$DOC_FILE
	echo "" >>$DOC_FILE
	echo "### Utility Functions" >>$DOC_FILE
	echo "Helper functions for various tasks." >>$DOC_FILE
	echo "" >>$DOC_FILE
	echo "### Hooks" >>$DOC_FILE
	echo "Custom React hooks for state management and side effects." >>$DOC_FILE
	echo "" >>$DOC_FILE
	echo "## Usage" >>$DOC_FILE
	echo "" >>$DOC_FILE
	echo "To use these components in the future:" >>$DOC_FILE
	echo "" >>$DOC_FILE
	echo "1. Copy the desired component to your project" >>$DOC_FILE
	echo "2. Install any required dependencies" >>$DOC_FILE
	echo "3. Import and use the component in your code" >>$DOC_FILE
	echo "" >>$DOC_FILE
	echo "## Dependencies" >>$DOC_FILE
	echo "" >>$DOC_FILE
	echo "These components may depend on the following libraries:" >>$DOC_FILE
	echo "" >>$DOC_FILE
	echo "- React" >>$DOC_FILE
	echo "- React DOM" >>$DOC_FILE
	echo "- Tailwind CSS" >>$DOC_FILE
	echo "- React Icons" >>$DOC_FILE
	echo "- React Router" >>$DOC_FILE
	echo "- i18next" >>$DOC_FILE
	echo "" >>$DOC_FILE
	echo "## License" >>$DOC_FILE
	echo "" >>$DOC_FILE
	echo "These components are subject to the same license as the original LibreChat project." >>$DOC_FILE

	echo "Created documentation: $DOC_FILE"
}

# Function to create an integration guide
create_integration_guide() {
	echo "Creating integration guide..."

	# Create integration guide file
	GUIDE_FILE="$PRESERVATION_DIR/INTEGRATION_GUIDE.md"

	echo "# LibreChat UI Components Integration Guide" >$GUIDE_FILE
	echo "" >>$GUIDE_FILE
	echo "This guide provides instructions for integrating preserved LibreChat UI components into Atlas-Chat." >>$GUIDE_FILE
	echo "" >>$GUIDE_FILE
	echo "## Prerequisites" >>$GUIDE_FILE
	echo "" >>$GUIDE_FILE
	echo "- Node.js and npm installed" >>$GUIDE_FILE
	echo "- Atlas-Chat project set up" >>$GUIDE_FILE
	echo "" >>$GUIDE_FILE
	echo "## Integration Steps" >>$GUIDE_FILE
	echo "" >>$GUIDE_FILE
	echo "### 1. Identify the Component to Integrate" >>$GUIDE_FILE
	echo "" >>$GUIDE_FILE
	echo "Browse the preserved components in this directory and identify the one you want to integrate." >>$GUIDE_FILE
	echo "" >>$GUIDE_FILE
	echo "### 2. Check Dependencies" >>$GUIDE_FILE
	echo "" >>$GUIDE_FILE
	echo "Examine the component file to identify any dependencies it requires. Install any missing dependencies:" >>$GUIDE_FILE
	echo "" >>$GUIDE_FILE
	echo '```bash' >>$GUIDE_FILE
	echo "npm install --save dependency-name" >>$GUIDE_FILE
	echo '```' >>$GUIDE_FILE
	echo "" >>$GUIDE_FILE
	echo "### 3. Copy the Component" >>$GUIDE_FILE
	echo "" >>$GUIDE_FILE
	echo "Copy the component file to the appropriate directory in your Atlas-Chat project:" >>$GUIDE_FILE
	echo "" >>$GUIDE_FILE
	echo '```bash' >>$GUIDE_FILE
	echo "cp /path/to/preserved/component.jsx /path/to/atlas-chat/frontend/client/src/components/" >>$GUIDE_FILE
	echo '```' >>$GUIDE_FILE
	echo "" >>$GUIDE_FILE
	echo "### 4. Update Imports" >>$GUIDE_FILE
	echo "" >>$GUIDE_FILE
	echo "Update any import statements in the component to match your project's structure." >>$GUIDE_FILE
	echo "" >>$GUIDE_FILE
	echo "### 5. Integrate with Atlas-Chat" >>$GUIDE_FILE
	echo "" >>$GUIDE_FILE
	echo "Import and use the component in your Atlas-Chat code:" >>$GUIDE_FILE
	echo "" >>$GUIDE_FILE
	echo '```jsx' >>$GUIDE_FILE
	echo "import PreservedComponent from './components/PreservedComponent';" >>$GUIDE_FILE
	echo "" >>$GUIDE_FILE
	echo "function MyComponent() {" >>$GUIDE_FILE
	echo "  return (" >>$GUIDE_FILE
	echo "    <div>" >>$GUIDE_FILE
	echo "      <PreservedComponent />" >>$GUIDE_FILE
	echo "    </div>" >>$GUIDE_FILE
	echo "  );" >>$GUIDE_FILE
	echo "}" >>$GUIDE_FILE
	echo '```' >>$GUIDE_FILE
	echo "" >>$GUIDE_FILE
	echo "### 6. Test the Integration" >>$GUIDE_FILE
	echo "" >>$GUIDE_FILE
	echo "Test the component to ensure it works correctly in your application." >>$GUIDE_FILE
	echo "" >>$GUIDE_FILE
	echo "### 7. Adapt as Needed" >>$GUIDE_FILE
	echo "" >>$GUIDE_FILE
	echo "You may need to adapt the component to fit your application's design and functionality." >>$GUIDE_FILE
	echo "" >>$GUIDE_FILE
	echo "## Common Integration Challenges" >>$GUIDE_FILE
	echo "" >>$GUIDE_FILE
	echo "- **Styling conflicts**: If you're using different styling approaches, you may need to adapt the component's styles." >>$GUIDE_FILE
	echo "- **State management**: Components may use different state management approaches than your application." >>$GUIDE_FILE
	echo "- **API integration**: Components may expect different API responses than your backend provides." >>$GUIDE_FILE
	echo "" >>$GUIDE_FILE
	echo "## Example: Integrating ChatMessage Component" >>$GUIDE_FILE
	echo "" >>$GUIDE_FILE
	echo "Here's an example of integrating the ChatMessage component:" >>$GUIDE_FILE
	echo "" >>$GUIDE_FILE
	echo "1. Copy the ChatMessage component:" >>$GUIDE_FILE
	echo '   `cp librechat_ui_components/components/Chat/ChatMessage/ChatMessage.jsx frontend/client/src/components/Chat/`' >>$GUIDE_FILE
	echo "" >>$GUIDE_FILE
	echo "2. Update imports in ChatMessage.jsx to match your project structure" >>$GUIDE_FILE
	echo "" >>$GUIDE_FILE
	echo "3. Import and use in your conversation component:" >>$GUIDE_FILE
	echo '   ```jsx' >>$GUIDE_FILE
	echo "   import ChatMessage from './ChatMessage';" >>$GUIDE_FILE
	echo "" >>$GUIDE_FILE
	echo "   function Conversation({ messages }) {" >>$GUIDE_FILE
	echo "     return (" >>$GUIDE_FILE
	echo '       <div className="conversation">' >>$GUIDE_FILE
	echo "         {messages.map(message => (" >>$GUIDE_FILE
	echo "           <ChatMessage key={message.id} message={message} />" >>$GUIDE_FILE
	echo "         ))}" >>$GUIDE_FILE
	echo "       </div>" >>$GUIDE_FILE
	echo "     );" >>$GUIDE_FILE
	echo "   }" >>$GUIDE_FILE
	echo '   ```' >>$GUIDE_FILE

	echo "Created integration guide: $GUIDE_FILE"
}

# Main execution
echo "Starting LibreChat UI preservation..."

# Run preservation functions
preserve_ui_components
preserve_styles
preserve_themes
create_manifest
create_documentation
create_integration_guide

echo "LibreChat UI preservation completed successfully!"
echo "Preserved components saved to: $PRESERVATION_DIR"

echo "Done!"
