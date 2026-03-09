import QtQuick 2.15
import QtQuick.Controls 2.15
import SddmComponents 2.0

Rectangle {
    id: root
    width: Screen.width
    height: Screen.height
    color: "#1e1e2e"

    Image {
        id: backgroundImage
        anchors.fill: parent
        source: ""
        fillMode: Image.PreserveAspectCrop
        visible: status === Image.Ready
    }

    Rectangle {
        anchors.fill: parent
        color: "#1e1e2e"
        opacity: backgroundImage.visible ? 0.7 : 1.0
    }

    Column {
        anchors.centerIn: parent
        spacing: 20
        width: 320

        Text {
            text: "Linta"
            color: "#00bcd4"
            font.pixelSize: 36
            font.family: "JetBrains Mono"
            font.bold: true
            anchors.horizontalCenter: parent.horizontalCenter
        }

        Text {
            text: "Lean by design."
            color: "#6c7086"
            font.pixelSize: 14
            font.family: "JetBrains Mono"
            anchors.horizontalCenter: parent.horizontalCenter
        }

        TextField {
            id: userField
            width: parent.width
            height: 44
            placeholderText: "Username"
            color: "#cdd6f4"
            font.pixelSize: 14
            font.family: "JetBrains Mono"
            background: Rectangle {
                color: "#282840"
                radius: 6
                border.color: userField.activeFocus ? "#00bcd4" : "#45475a"
                border.width: 1
            }
            text: userModel.lastUser
            KeyNavigation.tab: passwordField
            Keys.onReturnPressed: sddm.login(userField.text, passwordField.text, sessionModel.lastIndex)
        }

        TextField {
            id: passwordField
            width: parent.width
            height: 44
            placeholderText: "Password"
            echoMode: TextInput.Password
            color: "#cdd6f4"
            font.pixelSize: 14
            font.family: "JetBrains Mono"
            background: Rectangle {
                color: "#282840"
                radius: 6
                border.color: passwordField.activeFocus ? "#00bcd4" : "#45475a"
                border.width: 1
            }
            Keys.onReturnPressed: sddm.login(userField.text, passwordField.text, sessionModel.lastIndex)
        }

        Button {
            width: parent.width
            height: 44
            text: "Login"
            font.pixelSize: 14
            font.family: "JetBrains Mono"
            onClicked: sddm.login(userField.text, passwordField.text, sessionModel.lastIndex)
            background: Rectangle {
                color: parent.pressed ? "#009aaf" : "#00bcd4"
                radius: 6
            }
            contentItem: Text {
                text: parent.text
                color: "#1e1e2e"
                font: parent.font
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
            }
        }
    }

    Row {
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 20
        anchors.horizontalCenter: parent.horizontalCenter
        spacing: 20

        Text {
            text: Qt.formatDateTime(new Date(), "dddd, MMMM d")
            color: "#6c7086"
            font.pixelSize: 12
            font.family: "JetBrains Mono"
        }

        Text {
            text: Qt.formatTime(new Date(), "HH:mm")
            color: "#cdd6f4"
            font.pixelSize: 12
            font.family: "JetBrains Mono"
        }
    }
}
