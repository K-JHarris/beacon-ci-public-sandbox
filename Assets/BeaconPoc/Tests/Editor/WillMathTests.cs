using NUnit.Framework;
namespace Beacon.Poc.Tests
{
    public sealed class WillMathTests
    {
        [Test] public void RestoresExpectedAmount() => Assert.That(WillMath.Restore(10, 3, 120), Is.EqualTo(13));
        [Test] public void CapsAtCapacity() => Assert.That(WillMath.Restore(119, 10, 120), Is.EqualTo(120));
        [Test] public void ZeroGainLeavesValueUnchanged() => Assert.That(WillMath.Restore(5, 0, 120), Is.EqualTo(5));
        [Test] public void RejectsNegativeGain() => Assert.Throws<System.ArgumentOutOfRangeException>(() => WillMath.Restore(5, -1, 120));
    }
}
