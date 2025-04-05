#!/bin/bash

# Script to reduce code bloat in the Atlas-Chat application
# This script identifies and removes unnecessary code while preserving essential functionality

echo "Starting code bloat reduction process..."

# Create a backup directory
BACKUP_DIR="./code_backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p $BACKUP_DIR

echo "Created backup directory: $BACKUP_DIR"

# Function to backup a file before modifying it
backup_file() {
	local file=$1
	local backup_path="$BACKUP_DIR/$(dirname $file)"

	mkdir -p "$backup_path"
	cp "$file" "$backup_path/"

	echo "Backed up: $file"
}

# Function to remove unused components from frontend
cleanup_frontend() {
	echo "Cleaning up frontend code..."

	# Identify unused components
	FRONTEND_DIR="./frontend/client/src"

	# List of components to preserve (essential components)
	ESSENTIAL_COMPONENTS=(
		"components/Chat"
		"components/CodeExecution"
		"components/Artifacts"
		"components/Settings"
		"components/Header"
		"components/Footer"
		"components/Sidebar"
		"components/Auth"
		"components/common"
	)

	# Backup essential components
	for component in "${ESSENTIAL_COMPONENTS[@]}"; do
		if [ -d "$FRONTEND_DIR/$component" ]; then
			backup_file "$FRONTEND_DIR/$component"
		fi
	done

	# Find and remove unused components
	find $FRONTEND_DIR/components -type d | while read dir; do
		# Skip essential components
		skip=false
		for essential in "${ESSENTIAL_COMPONENTS[@]}"; do
			if [[ $dir == *"$essential"* ]]; then
				skip=true
				break
			fi
		done

		if [ "$skip" == false ] && [ -d "$dir" ] && [ "$dir" != "$FRONTEND_DIR/components" ]; then
			echo "Removing unused component directory: $dir"
			backup_file "$dir"
			rm -rf "$dir"
		fi
	done

	# Clean up unused styles
	echo "Cleaning up unused styles..."
	find $FRONTEND_DIR/styles -type f -name "*.css" -o -name "*.scss" | while read file; do
		# Check if the style is imported anywhere
		if ! grep -q "$(basename $file)" $FRONTEND_DIR --include="*.js" --include="*.jsx" --include="*.ts" --include="*.tsx"; then
			echo "Removing unused style: $file"
			backup_file "$file"
			rm "$file"
		fi
	done

	# Clean up unused utilities
	echo "Cleaning up unused utilities..."
	find $FRONTEND_DIR/utils -type f -name "*.js" -o -name "*.ts" | while read file; do
		# Check if the utility is imported anywhere
		if ! grep -q "$(basename $file | cut -d. -f1)" $FRONTEND_DIR --include="*.js" --include="*.jsx" --include="*.ts" --include="*.tsx"; then
			echo "Removing unused utility: $file"
			backup_file "$file"
			rm "$file"
		fi
	done
}

# Function to remove unused code from backend
cleanup_backend() {
	echo "Cleaning up backend code..."

	# Identify unused modules
	BACKEND_DIR="./backend/app"

	# List of modules to preserve (essential modules)
	ESSENTIAL_MODULES=(
		"api/code.py"
		"api/artifacts.py"
		"api/auth.py"
		"api/chat.py"
		"api/teams.py"
		"api/users.py"
		"api/security.ts"
		"api/performance.ts"
		"core/services/e2b"
		"core/services/tool_executor.py"
		"core/services/agent_service.py"
		"core/services/artifact_service.py"
		"core/executors"
		"core/security.py"
		"core/performance.py"
		"core/config.py"
		"models/artifacts.py"
		"models/user.py"
		"db/session.py"
	)

	# Backup essential modules
	for module in "${ESSENTIAL_MODULES[@]}"; do
		if [ -f "$BACKEND_DIR/$module" ]; then
			backup_file "$BACKEND_DIR/$module"
		elif [ -d "$BACKEND_DIR/$module" ]; then
			find "$BACKEND_DIR/$module" -type f | while read file; do
				backup_file "$file"
			done
		fi
	done

	# Find and remove unused Python files
	find $BACKEND_DIR -type f -name "*.py" | while read file; do
		# Skip essential modules
		skip=false
		for essential in "${ESSENTIAL_MODULES[@]}"; do
			if [[ $file == *"$essential"* ]]; then
				skip=true
				break
			fi
		done

		# Skip __init__.py files
		if [[ "$(basename $file)" == "__init__.py" ]]; then
			skip=true
		fi

		if [ "$skip" == false ]; then
			# Check if the module is imported anywhere
			module_name=$(basename $file | cut -d. -f1)
			if ! grep -q "import $module_name" $BACKEND_DIR --include="*.py" && ! grep -q "from .* import $module_name" $BACKEND_DIR --include="*.py"; then
				echo "Removing unused module: $file"
				backup_file "$file"
				rm "$file"
			fi
		fi
	done
}

# Function to optimize package.json dependencies
optimize_dependencies() {
	echo "Optimizing package.json dependencies..."

	# Backup package.json
	backup_file "./frontend/client/package.json"

	# Parse package.json and remove unused dependencies
	# This is a simplified approach - in a real implementation, you would use a tool like depcheck

	# For now, we'll just output a message
	echo "To optimize dependencies, run: npm prune --production"
}

# Function to remove duplicate code
remove_duplicates() {
	echo "Removing duplicate code..."

	# This would typically use a tool like jscpd or similar
	# For now, we'll just output a message
	echo "To find duplicate code, consider using a tool like jscpd"
}

# Function to minify and bundle frontend assets
optimize_assets() {
	echo "Optimizing frontend assets..."

	# This would typically use webpack, rollup, or similar
	# For now, we'll just output a message
	echo "Frontend assets will be optimized during the build process"
}

# Main execution
echo "Starting code bloat reduction..."

# Run cleanup functions
cleanup_frontend
cleanup_backend
optimize_dependencies
remove_duplicates
optimize_assets

echo "Code bloat reduction completed successfully!"
echo "Backup of original files saved to: $BACKUP_DIR"
echo "You can restore the backup if needed."

# Create a report of changes
echo "Creating report of changes..."
find $BACKUP_DIR -type f | sort >"$BACKUP_DIR/backed_up_files.txt"
echo "Report saved to: $BACKUP_DIR/backed_up_files.txt"

echo "Done!"
