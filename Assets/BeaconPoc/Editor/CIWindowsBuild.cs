using System;
using System.IO;
using UnityEditor;
using UnityEditor.Build.Reporting;
using UnityEditor.SceneManagement;
namespace Beacon.Poc
{
    public static class CIWindowsBuild
    {
        public static void Build()
        {
            Directory.CreateDirectory("Assets/BeaconPoc/Scenes");
            const string scenePath = "Assets/BeaconPoc/Scenes/PocScene.unity";
            var scene = EditorSceneManager.NewScene(NewSceneSetup.DefaultGameObjects, NewSceneMode.Single);
            if (!EditorSceneManager.SaveScene(scene, scenePath))
                throw new InvalidOperationException("Cannot save synthetic scene");
            Directory.CreateDirectory("build/StandaloneWindows64");
            var report = BuildPipeline.BuildPlayer(new BuildPlayerOptions
            {
                scenes = new[] { scenePath },
                locationPathName = "build/StandaloneWindows64/BeaconPoc.exe",
                target = BuildTarget.StandaloneWindows64,
                options = BuildOptions.None
            });
            if (report.summary.result != BuildResult.Succeeded)
                throw new InvalidOperationException("Windows build failed: " + report.summary.result);
        }
    }
}
