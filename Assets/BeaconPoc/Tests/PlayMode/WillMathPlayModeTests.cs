using System.Collections;
using NUnit.Framework;
using UnityEngine.TestTools;

namespace Beacon.Poc.Tests
{
    public sealed class WillMathPlayModeTests
    {
        [UnityTest]
        public IEnumerator OverflowProtectionPersistsAcrossFrames()
        {
            Assert.That(WillMath.Restore(int.MaxValue - 1, int.MaxValue, int.MaxValue),
                        Is.EqualTo(int.MaxValue),
                        "Overflow must be clamped before PlayMode advances");

            yield return null;

            Assert.That(WillMath.Restore(119, 10, 120), Is.EqualTo(120));
            Assert.Throws<System.ArgumentOutOfRangeException>(
                () => WillMath.Restore(5, -1, 120));
        }
    }
}
