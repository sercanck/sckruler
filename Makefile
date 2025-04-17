APP_NAME = Sckruler
SCRIPT = sckruler.py
ICON = icon.png
EXECUTABLE_PATH = dist/$(APP_NAME)
DESKTOP_FILE = $(APP_NAME).desktop

.PHONY: all build install clean uninstall

all: install clean



build:
#	pip install --user pyinstaller
	pyinstaller --onefile --windowed --name=$(APP_NAME) $(SCRIPT)

install: build
	@echo "Installing $(APP_NAME)..."
	install -Dm755 $(EXECUTABLE_PATH) ~/.local/bin/$(APP_NAME)
	install -Dm644 $(ICON) ~/.local/share/icons/$(APP_NAME).png
	@echo "Creating desktop entry..."
	mkdir -p ~/.local/share/applications
	echo "[Desktop Entry]" > ~/.local/share/applications/$(DESKTOP_FILE)
	echo "Name=$(APP_NAME)" >> ~/.local/share/applications/$(DESKTOP_FILE)
	echo "Exec=$(HOME)/.local/bin/$(APP_NAME)" >> ~/.local/share/applications/$(DESKTOP_FILE)
	echo "Icon=$(HOME)/.local/share/icons/$(APP_NAME).png" >> ~/.local/share/applications/$(DESKTOP_FILE)
	echo "Type=Application" >> ~/.local/share/applications/$(DESKTOP_FILE)
	echo "Categories=Utility;" >> ~/.local/share/applications/$(DESKTOP_FILE)
	echo "StartupNotify=false" >> ~/.local/share/applications/$(DESKTOP_FILE)
	echo "Terminal=false" >> ~/.local/share/applications/$(DESKTOP_FILE)
	chmod +x ~/.local/share/applications/$(DESKTOP_FILE)
	@echo "Done. You can now run $(APP_NAME) from the Applications menu."

clean:
	rm -rf build dist __pycache__ *.spec

uninstall:
	@echo "Uninstalling $(APP_NAME)..."
	rm -f ~/.local/bin/$(APP_NAME)
	rm -f ~/.local/share/icons/$(APP_NAME).png
	rm -f ~/.local/share/applications/$(DESKTOP_FILE)
